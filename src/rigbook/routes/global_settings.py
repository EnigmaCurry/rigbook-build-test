import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rigbook.db import (
    GLOBAL_DEFAULTABLE_KEYS,
    GLOBAL_ONLY_KEYS,
    MetaSetting,
    get_meta_session,
)

logger = logging.getLogger("rigbook")

router = APIRouter(prefix="/api/global-settings", tags=["global-settings"])

ALLOWED_KEYS = GLOBAL_DEFAULTABLE_KEYS | GLOBAL_ONLY_KEYS
HIDDEN_KEYS = {"qrz_password", "hamalert_password"}


class SettingValue(BaseModel):
    value: str


class SettingResponse(BaseModel):
    key: str
    value: str | None

    model_config = {"from_attributes": True}


def _redact(setting: MetaSetting) -> SettingResponse:
    if setting.key in HIDDEN_KEYS:
        return SettingResponse(key=setting.key, value="***" if setting.value else None)
    return SettingResponse.model_validate(setting)


@router.get("/", response_model=list[SettingResponse])
async def list_global_settings(meta: AsyncSession = Depends(get_meta_session)):
    result = await meta.execute(select(MetaSetting))
    return [_redact(s) for s in result.scalars().all()]


@router.get("/{key}", response_model=SettingResponse)
async def get_global_setting(key: str, meta: AsyncSession = Depends(get_meta_session)):
    result = await meta.execute(select(MetaSetting).where(MetaSetting.key == key))
    setting = result.scalar_one_or_none()
    if not setting:
        return SettingResponse(key=key, value=None)
    return _redact(setting)


@router.put("/{key}", response_model=SettingResponse)
async def upsert_global_setting(
    key: str,
    data: SettingValue,
    meta: AsyncSession = Depends(get_meta_session),
):
    if key not in ALLOWED_KEYS:
        raise HTTPException(
            status_code=400,
            detail=f"Key '{key}' is not a valid global setting",
        )
    result = await meta.execute(select(MetaSetting).where(MetaSetting.key == key))
    setting = result.scalar_one_or_none()
    if setting:
        if setting.value == data.value:
            return _redact(setting)
        setting.value = data.value
    else:
        setting = MetaSetting(key=key, value=data.value)
        meta.add(setting)
    await meta.commit()
    await meta.refresh(setting)
    log_value = "***" if key in HIDDEN_KEYS else data.value
    logger.info("Global setting changed: %s = %s", key, log_value)
    return _redact(setting)

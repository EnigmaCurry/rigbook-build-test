import time

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from rigbook.db import PotaLocation, PotaPark, PotaProgram, get_session

router = APIRouter(prefix="/api/pota", tags=["pota"])

POTA_SPOTS_URL = "https://api.pota.app/v1/spots"
POTA_PROGRAMS_URL = "https://api.pota.app/programs"
POTA_LOCATIONS_URL = "https://api.pota.app/locations"
POTA_LOCATION_PARKS_URL = "https://api.pota.app/location/parks"

TTL = 86400  # 24 hours


@router.get("/spots")
async def get_spots():
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(
            POTA_SPOTS_URL,
            headers={"Accept": "application/json"},
        )
        res.raise_for_status()
        return res.json()


async def _fetch_and_cache_programs(session: AsyncSession):
    now = time.time()
    async with httpx.AsyncClient(timeout=30) as client:
        prog_res, loc_res = await _fetch_programs_and_locations(client)

    await session.execute(delete(PotaProgram))
    await session.execute(delete(PotaLocation))

    for p in prog_res:
        session.add(
            PotaProgram(
                program_id=p.get("programId", 0),
                prefix=p.get("programPrefix", ""),
                name=p.get("programName", ""),
                fetched_at=now,
            )
        )

    for loc in loc_res:
        descriptor = loc.get("locationDesc", "")
        prefix = descriptor.split("-")[0] if "-" in descriptor else descriptor
        session.add(
            PotaLocation(
                location_id=loc.get("locationId", 0),
                program_prefix=prefix,
                descriptor=descriptor,
                name=loc.get("locationName", ""),
                latitude=loc.get("latitude"),
                longitude=loc.get("longitude"),
                fetched_at=now,
            )
        )

    await session.commit()


async def _fetch_programs_and_locations(client: httpx.AsyncClient):
    prog_res = await client.get(
        POTA_PROGRAMS_URL, headers={"Accept": "application/json"}
    )
    prog_res.raise_for_status()

    loc_res = await client.get(
        POTA_LOCATIONS_URL, headers={"Accept": "application/json"}
    )
    loc_res.raise_for_status()

    return prog_res.json(), loc_res.json()


@router.get("/programs")
async def get_programs(session: AsyncSession = Depends(get_session)):
    row = (
        await session.execute(
            select(func.min(PotaProgram.fetched_at))
        )
    ).scalar()

    if row is None or time.time() - row > TTL:
        await _fetch_and_cache_programs(session)

    programs = (await session.execute(select(PotaProgram))).scalars().all()

    # Count locations per program prefix
    loc_counts = dict(
        (
            await session.execute(
                select(PotaLocation.program_prefix, func.count()).group_by(
                    PotaLocation.program_prefix
                )
            )
        ).all()
    )

    return [
        {
            "program_id": p.program_id,
            "prefix": p.prefix,
            "name": p.name,
            "location_count": loc_counts.get(p.prefix, 0),
            "cached": True,
        }
        for p in programs
    ]


@router.get("/programs/{prefix}/locations")
async def get_locations(
    prefix: str, session: AsyncSession = Depends(get_session)
):
    locations = (
        (
            await session.execute(
                select(PotaLocation).where(PotaLocation.program_prefix == prefix)
            )
        )
        .scalars()
        .all()
    )

    # Count parks per location descriptor
    descriptors = [loc.descriptor for loc in locations]
    park_counts = {}
    if descriptors:
        rows = (
            await session.execute(
                select(PotaPark.location_desc, func.count()).where(
                    PotaPark.location_desc.in_(descriptors)
                ).group_by(PotaPark.location_desc)
            )
        ).all()
        park_counts = dict(rows)

    return [
        {
            "location_id": loc.location_id,
            "descriptor": loc.descriptor,
            "name": loc.name,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "park_count": park_counts.get(loc.descriptor, 0),
        }
        for loc in locations
    ]


@router.get("/locations/{descriptor}/parks")
async def get_parks(
    descriptor: str, session: AsyncSession = Depends(get_session)
):
    row = (
        await session.execute(
            select(func.min(PotaPark.fetched_at)).where(
                PotaPark.location_desc == descriptor
            )
        )
    ).scalar()

    if row is None or time.time() - row > TTL:
        await _fetch_and_cache_parks(session, descriptor)

    parks = (
        (
            await session.execute(
                select(PotaPark).where(PotaPark.location_desc == descriptor)
            )
        )
        .scalars()
        .all()
    )

    return [
        {
            "reference": p.reference,
            "name": p.name,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "grid": p.grid,
            "attempts": p.attempts,
            "activations": p.activations,
            "qsos": p.qsos,
        }
        for p in parks
    ]


async def _fetch_and_cache_parks(session: AsyncSession, descriptor: str):
    now = time.time()
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.get(
            f"{POTA_LOCATION_PARKS_URL}/{descriptor}",
            headers={"Accept": "application/json"},
        )
        res.raise_for_status()
        parks_data = res.json()

    await session.execute(
        delete(PotaPark).where(PotaPark.location_desc == descriptor)
    )

    for p in parks_data:
        session.add(
            PotaPark(
                reference=p.get("reference", ""),
                name=p.get("name", ""),
                location_desc=descriptor,
                latitude=p.get("latitude"),
                longitude=p.get("longitude"),
                grid=p.get("grid"),
                attempts=p.get("attempts"),
                activations=p.get("activations"),
                qsos=p.get("qsos"),
                fetched_at=now,
            )
        )

    await session.commit()


@router.post("/refresh/programs")
async def refresh_programs(session: AsyncSession = Depends(get_session)):
    await _fetch_and_cache_programs(session)
    return {"status": "ok"}


@router.post("/refresh/locations/{descriptor}")
async def refresh_location_parks(
    descriptor: str, session: AsyncSession = Depends(get_session)
):
    await _fetch_and_cache_parks(session, descriptor)
    return {"status": "ok"}

import pycountry
from fastapi import APIRouter

router = APIRouter(prefix="/api/geo", tags=["geo"])


@router.get("/countries")
async def list_countries():
    return [
        {"code": c.alpha_2, "name": c.name}
        for c in sorted(pycountry.countries, key=lambda c: c.name)
    ]


@router.get("/subdivisions/{country_code}")
async def list_subdivisions(country_code: str):
    subs = pycountry.subdivisions.get(country_code=country_code.upper())
    if not subs:
        return []
    return [
        {"code": s.code, "name": s.name, "type": s.type}
        for s in sorted(subs, key=lambda s: s.name)
    ]

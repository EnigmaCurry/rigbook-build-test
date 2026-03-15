from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from rigbook.db import init_db
from rigbook.routes.contacts import router as contacts_router
from rigbook.routes.settings import router as settings_router
from rigbook.flrig import router as flrig_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Rigbook", lifespan=lifespan)

app.include_router(contacts_router)
app.include_router(settings_router)
app.include_router(flrig_router)

static_dir = Path(__file__).parent / "static"
if static_dir.is_dir():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


def run() -> None:
    uvicorn.run("rigbook.main:app", host="0.0.0.0", port=8073)

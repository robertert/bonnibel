from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine
from app.modules.notification import models as notification_models
from app.modules.notification.manager import notification_service
from app.modules.notification.router import router as notification_router
from app.modules.notification.ws import router as notification_ws_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    _ = notification_models
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        notification_service.seed_demo_data(db)
    yield


settings = get_settings()

app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notification_router)
app.include_router(notification_ws_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

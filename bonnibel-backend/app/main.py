from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.modules.tasks_and_users.router import router as tasks_and_users_router


app = FastAPI(title="Bonnibel Backend")

app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.cors_origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
	init_db()


app.include_router(tasks_and_users_router)


@app.get("/health")
def health() -> dict[str, str]:
	return {"status": "ok"}


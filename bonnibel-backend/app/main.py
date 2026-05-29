from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.auth.router import router as auth_router
from app.modules.logic.router import router as project_router

# FastAPI app init
app = FastAPI(
    title="Bonnibel API",
    description="Backend dla systemu zarządzania postępem prac zespołu Bonnibel",
    version="1.0.0"
)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])

app.include_router(project_router)  # prefix już ustawiony w routerze

# (Health Check)
@app.get("/api/health", tags=["System"])
def health_check():
    return {"status": "ok", "message": "Bonnibel API działa poprawnie"}


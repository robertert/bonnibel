from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.auth.router import router as auth_router
from app.modules.docs.router import router as docs_router
from app.modules.pr.router import router as pr_router

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
app.include_router(docs_router, prefix="/api", tags=["Docs"])
app.include_router(pr_router, prefix="/api", tags=["Pull Requests"])

# (Health Check)
@app.get("/api/health", tags=["System"])
async def health_check():
    return {"status": "ok", "message": "Bonnibel API działa poprawnie"}

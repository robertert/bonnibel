from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.auth.router import router as auth_router
from app.modules.chat.router import router as chat_router
from app.modules.analytics.router import router as analytics_router
from app.modules.tasks_and_users.router import router as tasks_and_users_router
from app.modules.logic.router import router as project_router
from app.modules.notification.router import router as notification_router
from app.modules.notification.ws import router as notification_ws_router

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
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(analytics_router, prefix="/api", tags=["Analytics"])
app.include_router(tasks_and_users_router, prefix="/api", tags=["Tasks & Users"])

app.include_router(project_router)  # prefix już ustawiony w routerze

app.include_router(notification_router, prefix="/api", tags=["Notifications"])
app.include_router(notification_ws_router, prefix="/api", tags=["Notifications"])

# (Health Check)
@app.get("/api/health", tags=["System"])
def health_check():
    return {"status": "ok", "message": "Bonnibel API działa poprawnie"}

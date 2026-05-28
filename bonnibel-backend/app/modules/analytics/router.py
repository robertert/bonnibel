from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.analytics.service import AnalyticsService

router = APIRouter(prefix="/projects/{project_id}/analytics")

service = AnalyticsService()


@router.get("/overview")
async def overview(project_id: int, db: Session = Depends(get_db)):
    return await service.get_overview(db, project_id)
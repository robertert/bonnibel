from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.core.models import ProjectRole, IntegrationProvider


# Projects
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    project_id: int
    owner_id: str
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True


class ProjectSummary(BaseModel):
    project_id: int
    name: str
    description: Optional[str]
    owner_id: str

    class Config:
        from_attributes = True


# Integrations
class ProjectIntegrationCreate(BaseModel):
    provider: IntegrationProvider
    external_id: str
    access_token: str


class ProjectIntegrationResponse(BaseModel):
    integration_id: int
    project_id: int
    provider: IntegrationProvider
    external_id: str
    is_active: bool

    class Config:
        from_attributes = True


# Membership
class ProjectMemberCreate(BaseModel):
    user_id: str
    role: ProjectRole


class ProjectMemberResponse(BaseModel):
    project_id: int
    user_id: str
    role: ProjectRole

    class Config:
        from_attributes = True


class MemberRoleUpdate(BaseModel):
    role: ProjectRole
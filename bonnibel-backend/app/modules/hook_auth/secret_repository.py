from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models import IntegrationProvider, WebhookSecret


class SecretRepository:
    """Dostęp do aktywnych sekretów webhooków (tabela webhook_secrets)."""

    def __init__(self, db: Session):
        self.db = db

    def get_active_secret(self, project_id: int, provider: IntegrationProvider) -> str | None:
        row = self.db.scalars(
            select(WebhookSecret).where(
                WebhookSecret.project_id == project_id,
                WebhookSecret.provider == provider,
                WebhookSecret.is_active.is_(True),
            )
        ).first()
        return row.secret if row else None

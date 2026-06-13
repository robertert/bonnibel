from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.models import IntegrationProvider
from app.modules.hook_auth.secret_repository import SecretRepository
from app.modules.hook_auth.verifier import SignatureVerifierFactory

# Mapowanie nazwy z URL na dostawcę z modelu.
_PROVIDER_ALIASES = {
    "git": IntegrationProvider.GITHUB,
    "github": IntegrationProvider.GITHUB,
    "jira": IntegrationProvider.JIRA,
}


def resolve_provider(provider: str) -> IntegrationProvider:
    key = provider.lower()
    if key not in _PROVIDER_ALIASES:
        raise ValueError(f"Unsupported webhook provider: {provider}")
    return _PROVIDER_ALIASES[key]


class HookAuthService:
    """Orkiestruje weryfikację autentyczności webhooka: sekret + podpis."""

    def __init__(self, db: Session):
        self.secrets = SecretRepository(db)

    def verify(self, provider: IntegrationProvider, project_id: int, payload: bytes, signature: str) -> bool:
        secret = self.secrets.get_active_secret(project_id, provider)
        if not secret:
            return False
        verifier = SignatureVerifierFactory.for_provider(provider.value)
        return verifier.verify(payload, signature, secret)

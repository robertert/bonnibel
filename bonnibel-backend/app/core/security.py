from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt import PyJWTError

from app.core.config import get_settings


def create_access_token(user_id: str, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + (expires_delta or timedelta(hours=8))
    payload: dict[str, Any] = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except PyJWTError:
        return None

    user_id = payload.get("sub")
    return user_id if isinstance(user_id, str) and user_id else None

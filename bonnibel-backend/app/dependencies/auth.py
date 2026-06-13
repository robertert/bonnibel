from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.models import User
from app.core.security import decode_access_token

# auto_error=True -> brak/niepoprawny nagłówek Authorization zwróci 403/401 zanim wejdziemy do funkcji.
bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Wyciąga zalogowanego użytkownika z tokenu JWT (Authorization: Bearer ...)."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exc
    except jwt.PyJWTError:
        raise credentials_exc

    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise credentials_exc
    return user


def get_current_user_id(user: User = Depends(get_current_user)) -> str:
    """Zwraca samo user_id zalogowanego użytkownika (dla modułów operujących na id)."""
    return user.user_id


CurrentUserId = Annotated[str, Depends(get_current_user_id)]

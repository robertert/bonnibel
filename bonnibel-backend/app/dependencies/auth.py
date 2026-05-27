from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    x_user_id: Annotated[
        str | None,
        Header(
            alias="X-User-Id",
            description="Demo auth header. Use one of: user-1, user-2, user-3.",
            examples=["user-1"],
        ),
    ] = None,
) -> str:
    if credentials:
        user_id = decode_access_token(credentials.credentials)
        if user_id:
            return user_id

    if x_user_id:
        return x_user_id

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid authentication credentials",
    )


CurrentUserId = Annotated[str, Depends(get_current_user_id)]

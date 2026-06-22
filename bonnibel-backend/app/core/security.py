from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt  # Zmiana z passlib

SECRET_KEY = "twoj-bardzo-tajny-klucz-zmien-go-na-produkcji"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    # Rzuca jwt.PyJWTError (np. ExpiredSignatureError, InvalidTokenError) przy błędnym tokenie.
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

from typing import List
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.models import User, ProjectMember, ProjectRole
from app.core.security import SECRET_KEY, ALGORITHM

# Definicja schematu autoryzacji (wskazuje, skąd Swagger UI ma pobierać token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise credentials_exception
        
    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[ProjectRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ProjectMember:
        # Odpytanie bazy danych o relację między użytkownikiem a projektem
        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.user_id
        ).first()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="User is not a member of this project"
            )

        if member.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Operation not permitted. Required roles: {[r.value for r in self.allowed_roles]}"
            )

        # Zwrócenie obiektu członkostwa może być przydatne w dalszej logice endpointu
        return member
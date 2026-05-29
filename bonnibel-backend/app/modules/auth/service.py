import uuid
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.models import User, Auth, RefreshToken
from app.core.security import get_password_hash, verify_password, create_access_token
from app.modules.auth.schemas import UserCreate, UserLogin

def register_user(db: Session, user_in: UserCreate):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email is already registered"
        )
    
    user_id = uuid.uuid4().hex
    
    db_user = User(
        user_id=user_id,
        email=user_in.email,
        name=user_in.name,
        surname=user_in.surname
    )
    db.add(db_user)
    
    db_auth = Auth(
        user_id=user_id,
        pass_hash=get_password_hash(user_in.password)
    )
    db.add(db_auth)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def login_user(db: Session, login_data: UserLogin):
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not user.auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
    
    if not verify_password(login_data.password, user.auth.pass_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
    
    access_token = create_access_token(data={"sub": user.user_id})
    refresh_token_str = secrets.token_urlsafe(32)
    
    db_token = RefreshToken(
        user_id=user.user_id,
        token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(db_token)
    db.refresh(user)
    db.commit()
    
    return {
        "user_id": user.user_id,
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer"
    }

def refresh_access_token(db: Session, refresh_token: str):
    db_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()

    if not db_token or db_token.is_revoked or db_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or expired refresh token"
        )
    
    new_access_token = create_access_token(data={"sub": db_token.user.user_id})
    new_refresh_token_str = secrets.token_urlsafe(32)

    new_db_token = RefreshToken(
        user_id=db_token.user.user_id,
        token=new_refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(new_db_token)
    db.delete(db_token)
    db.commit()

    return {
        "user_id": db_token.user.user_id,
        "access_token": new_access_token,
        "refresh_token": new_refresh_token_str,
        "token_type": "bearer"
    }

def logout_user(db: Session, refresh_token: str):
    db_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )

    db.delete(db_token)
    db.commit()

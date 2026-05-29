from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth import schemas, service

router = APIRouter()


@router.post("/register", status_code=201)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    user = service.register_user(db, user_in)
    return {"message": "User created successfully", "user_id": user.user_id}


@router.post("/login", response_model=schemas.TokenResponse, response_model_by_alias=True)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    return service.login_user(db, login_data)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.user import UserCreate, UserLogin, UserOut, Token
from app.services import user_service
from app.auth.security import create_access_token
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """Creates a new account. Fails with 400 if the email is already taken."""
    existing = user_service.get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )
    user = user_service.create_user(
        db, full_name=payload.full_name, email=payload.email, password=payload.password
    )
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """Verifies email+password and returns a JWT the frontend stores and sends on future requests."""
    user = user_service.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Protected route — only reachable with a valid Bearer token. Returns the logged-in user's info."""
    return current_user

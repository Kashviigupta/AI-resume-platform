from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserCreate(BaseModel):
    """Shape of the JSON body the frontend sends to POST /auth/register."""

    full_name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    """Shape of the JSON body the frontend sends to POST /auth/login."""

    email: EmailStr
    password: str


class UserOut(BaseModel):
    """
    What we send BACK to the frontend. Notice hashed_password is never
    included here — this is what keeps it from ever leaking into an API
    response, even though it's a real column on the User model.
    """

    id: int
    full_name: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # lets us return an ORM User object directly


class Token(BaseModel):
    """Shape of the JSON response from POST /auth/login."""

    access_token: str
    token_type: str = "bearer"

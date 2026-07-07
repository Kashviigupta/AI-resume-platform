from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.auth.security import decode_access_token
from app.models.user import User

# Reads the "Authorization: Bearer <token>" header the frontend's axios
# interceptor already attaches to every request (see services/api.js).
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Drop this as a dependency on any route that should require login:
        def my_route(current_user: User = Depends(get_current_user)):
    FastAPI runs it before the route body; if the token is missing/invalid/
    expired, the request never reaches your route logic at all.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user

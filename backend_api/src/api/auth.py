"""Authentication utilities: password hashing/check, JWT creation/validation, login dependency."""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from sqlalchemy.orm import Session
from . import models, schemas, database

import os

# Settings (should be in .env)
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# PUBLIC_INTERFACE
def verify_password(plain_password, hashed_password):
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

# PUBLIC_INTERFACE
def get_password_hash(password):
    """Hash a password for storing."""
    return pwd_context.hash(password)

# PUBLIC_INTERFACE
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Generate a JWT token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# PUBLIC_INTERFACE
def get_user_by_username(db: Session, username: str):
    """Return user by username."""
    return db.query(models.User).filter(models.User.username == username).first()

# PUBLIC_INTERFACE
def authenticate_user(db: Session, username: str, password: str):
    """Authenticate and return user, or None."""
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

# PUBLIC_INTERFACE
async def get_current_user(db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    """FastAPI dependency to fetch the user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

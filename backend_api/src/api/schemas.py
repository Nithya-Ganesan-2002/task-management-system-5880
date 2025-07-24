"""Pydantic models for API (request/response) validation."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# User schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, description="Unique username for registration")
    email: EmailStr
    password: str = Field(..., min_length=5)

class UserLogin(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

# Task schemas
class TaskBase(BaseModel):
    title: str = Field(..., max_length=150, description="Title of the task")
    description: Optional[str] = Field(None, description="Description of the task")
    is_completed: Optional[bool] = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None

class TaskRead(TaskBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

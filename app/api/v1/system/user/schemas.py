from typing import List, Optional
from pydantic import BaseModel, Field

EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


class UserCreate(BaseModel):
    username: str
    email: str = Field(..., pattern=EMAIL_PATTERN)
    password: str
    is_active: Optional[bool] = True


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = Field(None, pattern=EMAIL_PATTERN)
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True


class UserList(BaseModel):
    total: int
    items: List[UserResponse]

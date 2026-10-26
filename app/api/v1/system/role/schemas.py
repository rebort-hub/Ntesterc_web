from typing import List, Optional
from pydantic import BaseModel


class RoleCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None


class RoleResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class RoleList(BaseModel):
    total: int
    items: List[RoleResponse]

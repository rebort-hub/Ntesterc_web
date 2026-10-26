from typing import List, Optional

from pydantic import BaseModel, field_validator

from app.api.v1.system.permission.model import PERMISSION_OPEN_TYPES, PERMISSION_TYPES


class PermissionCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    type: str
    path: Optional[str] = None
    icon: Optional[str] = None
    open_type: Optional[str] = None
    is_enabled: bool = True
    parent_id: Optional[int] = None
    sort_order: Optional[int] = 0

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in PERMISSION_TYPES:
            raise ValueError(f"invalid permission type: {list(PERMISSION_TYPES)}")
        return v

    @field_validator("open_type")
    @classmethod
    def validate_open_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        if v not in PERMISSION_OPEN_TYPES:
            raise ValueError(f"invalid open_type: {list(PERMISSION_OPEN_TYPES)}")
        return v


class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    path: Optional[str] = None
    icon: Optional[str] = None
    open_type: Optional[str] = None
    is_enabled: Optional[bool] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if v not in PERMISSION_TYPES:
            raise ValueError(f"invalid permission type: {list(PERMISSION_TYPES)}")
        return v

    @field_validator("open_type")
    @classmethod
    def validate_open_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        if v not in PERMISSION_OPEN_TYPES:
            raise ValueError(f"invalid open_type: {list(PERMISSION_OPEN_TYPES)}")
        return v


class PermissionResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    type: str
    path: Optional[str] = None
    icon: Optional[str] = None
    open_type: Optional[str] = None
    is_enabled: bool = True
    parent_id: Optional[int] = None
    sort_order: int

    class Config:
        from_attributes = True


class PermissionTreeNode(PermissionResponse):
    children: List["PermissionTreeNode"] = []


class PermissionList(BaseModel):
    total: int
    items: List[PermissionResponse]

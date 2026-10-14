from typing import List, Optional

from pydantic import BaseModel


class PermissionCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    type: str
    path: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = 0


class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    path: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None


class PermissionResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    type: str
    path: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: int

    class Config:
        from_attributes = True


class PermissionTreeNode(PermissionResponse):
    children: List["PermissionTreeNode"] = []


class PermissionList(BaseModel):
    total: int
    items: List[PermissionResponse]

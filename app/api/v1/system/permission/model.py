from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.models.base import ModelBase
from app.api.v1.system.role.model import role_permission

# directory=目录 menu=菜单 button=按钮 api=接口
PERMISSION_TYPES = ("directory", "menu", "button", "api")
# _self=当前页 _blank=新窗口 _iframe=框架页签
PERMISSION_OPEN_TYPES = ("_self", "_blank", "_iframe")


class Permission(ModelBase):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    code: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(20))
    path: Mapped[str | None] = mapped_column(String(200), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(80), nullable=True)
    open_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # 启用后目录/菜单才会出现在侧栏
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("permissions.id", ondelete="SET NULL"), nullable=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    parent: Mapped["Permission | None"] = relationship(
        "Permission", remote_side="Permission.id", back_populates="children"
    )
    children: Mapped[list["Permission"]] = relationship(
        "Permission", back_populates="parent"
    )
    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary=role_permission, back_populates="permissions"
    )

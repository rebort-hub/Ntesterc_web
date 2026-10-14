from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import Base, TimestampMixin


class UserRole(Base, TimestampMixin):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )
    data_scope: Mapped[str] = mapped_column(String(20), default="self")

    user: Mapped["User"] = relationship("User", back_populates="user_roles")  # type: ignore[name-defined]
    role: Mapped["Role"] = relationship("Role", back_populates="user_roles")  # type: ignore[name-defined]

from typing import Any
from sqlalchemy import Integer, String, JSON
from sqlalchemy.orm import mapped_column, relationship, Mapped

from app.db.session import Base


class Permission(Base):
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    resource: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    conditions: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    users: Mapped[list['User']] = relationship('User', secondary='user_permissions', back_populates='direct_permissions')
    roles: Mapped[list['Role']] = relationship('Role', secondary='role_permissions', back_populates='permissions')

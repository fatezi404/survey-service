from datetime import datetime
from sqlalchemy import Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import mapped_column, relationship, Mapped

from app.db.session import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False) # fixme: default=False since user has to approve account creation via email
    account_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True, server_default=func.now())

    direct_permissions: Mapped[list['Permission']] = relationship('Permission', secondary='user_permissions', back_populates='users')
    roles: Mapped[list['Role']] = relationship('Role', secondary='user_roles', back_populates='users')

from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, relationship, Mapped

from app.db.session import Base
from app.models.association_tables import user_roles, role_permissions


class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    users: Mapped[list['User']] = relationship('User', secondary=user_roles, back_populates='roles')
    permissions: Mapped[list['Permission']] = relationship('Permission', secondary=role_permissions, back_populates='roles')

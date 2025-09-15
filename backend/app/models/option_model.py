from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, Mapped

from app.db.session import Base


class Option(Base):
    __tablename__ = 'options'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False, index=True)
    text: Mapped[str] = mapped_column(String, nullable=False)

    question: Mapped['Question'] = relationship('Question', back_populates='options')

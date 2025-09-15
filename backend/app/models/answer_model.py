from sqlalchemy import Integer, ForeignKey, Text
from sqlalchemy.orm import mapped_column, relationship, Mapped

from app.db.session import Base


class Answer(Base):
    __tablename__ = 'answers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    response_id: Mapped[int] = mapped_column(Integer, ForeignKey('responses.id'), nullable=False, index=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey('questions.id'), nullable=False, index=True)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    option_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('options.id'), nullable=True, index=True)

    response: Mapped['Response'] = relationship('Response', back_populates='answers')

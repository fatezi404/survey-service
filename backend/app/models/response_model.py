from datetime import datetime
from sqlalchemy import Integer, ForeignKey, func, DateTime
from sqlalchemy.orm import mapped_column, relationship, Mapped

from app.db.session import Base


class Response(Base):
    __tablename__ = 'responses'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    survey_id: Mapped[int] = mapped_column(Integer, ForeignKey('surveys.id'), nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id'), nullable=True, index=True) # true if user is anonymous
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True, server_default=func.now())

    answers: Mapped[list['Answer']] = relationship('Answer', back_populates='response')
    survey: Mapped['Survey'] = relationship('Survey', back_populates='responses')

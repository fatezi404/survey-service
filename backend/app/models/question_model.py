from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, Mapped

from app.db.session import Base
from app.core.config import QuestionType


class Question(Base):
    __tablename__ = 'questions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    survey_id: Mapped[int] = mapped_column(Integer, ForeignKey('surveys.id', ondelete='CASCADE'))
    text: Mapped[str] = mapped_column(String, nullable=False, index=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    survey: Mapped['Survey'] = relationship('Survey', back_populates='questions')
    options: Mapped[list['Option']] = relationship('Option', back_populates='question')

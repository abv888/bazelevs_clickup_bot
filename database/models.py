from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now(), onupdate=datetime.now())


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer)
    clickup_id = Column(Integer)
    clickup_api_token = Column(String)

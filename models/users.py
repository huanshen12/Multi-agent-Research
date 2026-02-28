from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from config.db_conf import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))

class Token(Base):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), index=True)
    token: Mapped[str] = mapped_column(String(255))
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


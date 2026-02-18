from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from config.db_conf import Base
from models.users import User


class Report(Base):
    __tablename__ = "reports"

    id:Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id:Mapped[int] = mapped_column(Integer, ForeignKey(User.id),index=True)
    topic:Mapped[str] = mapped_column(String(255), index=True)
    content:Mapped[str] = mapped_column(Text)
    created_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

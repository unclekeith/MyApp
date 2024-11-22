from database.core import Base
from sqlalchemy import Date, Integer, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column


class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String, nullable=True, index=True)
    start_time: Mapped[Time] = mapped_column(Time, nullable=False)
    end_time: Mapped[Time] = mapped_column(Time, nullable=False)
    date: Mapped[Date] = mapped_column(Date, default=func.now())

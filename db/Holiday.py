from . import Base
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column
from datetime import date, datetime
from sqlalchemy import func, ForeignKey, Enum, Column, BigInteger
import enum
from typing import List


class StatusHoliday(enum.Enum):
    waiting = "waiting"
    ready_list = "ready_list"
    complete = "complete"


class Holiday(Base):
    __tablename__ = "holiday"

    id: Mapped[int] = mapped_column(primary_key=True)
    birthday_boy_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("employee.id"))
    responsible_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("employee.id"), nullable=True)
    gift_amount: Mapped[int] = mapped_column(nullable=True)
    holiday_date: Mapped[date]
    status = Column(Enum(StatusHoliday), default=StatusHoliday.waiting)
    record_time: Mapped[datetime] = mapped_column(server_default=func.now())

    birthday_boy: Mapped["Employee"] = relationship(back_populates="holidays_bb", foreign_keys=[birthday_boy_id])
    responsible: Mapped["Employee"] = relationship(back_populates="holidays_res", foreign_keys=[responsible_id])
    participants: Mapped[List["Participant"]] = relationship(back_populates="holiday", passive_deletes=True,
                                                             order_by="Participant.id")

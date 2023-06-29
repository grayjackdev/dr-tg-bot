from . import Base
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column
from datetime import date, datetime
from sqlalchemy import func, BigInteger
from typing import List



class Employee(Base):
    __tablename__ = "employee"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fio: Mapped[str]
    birthday: Mapped[date]
    photo: Mapped[str]
    details: Mapped[str]
    record_time: Mapped[datetime] = mapped_column(server_default=func.now())

    wishes: Mapped[List["Wish"]] = relationship(back_populates="employee")
    holidays_bb: Mapped[List["Holiday"]] = relationship(back_populates="birthday_boy", foreign_keys = 'Holiday.birthday_boy_id', order_by="desc(Holiday.holiday_date)")
    holidays_res: Mapped[List["Holiday"]] = relationship(back_populates="responsible", foreign_keys = 'Holiday.responsible_id', order_by="desc(Holiday.holiday_date)")
    participants: Mapped[List["Participant"]] = relationship(back_populates="employee")








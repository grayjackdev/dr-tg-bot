from . import Base
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column
from datetime import date, datetime
from sqlalchemy import func
from typing import List



class Employee(Base):
    __tablename__ = "employee"

    id: Mapped[int] = mapped_column(primary_key=True)
    fio: Mapped[str]
    birthday: Mapped[date]
    photo: Mapped[str]
    details: Mapped[str]
    record_time: Mapped[datetime] = mapped_column(server_default=func.now())

    wishes: Mapped[List["Wish"]] = relationship(back_populates="employee")







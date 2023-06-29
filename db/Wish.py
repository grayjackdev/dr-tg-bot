from . import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship
from datetime import date, datetime
from sqlalchemy import func
from sqlalchemy import ForeignKey, BigInteger



class Wish(Base):
    __tablename__ = "wish"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("employee.id"))
    text: Mapped[str]
    record_time: Mapped[datetime] = mapped_column(server_default=func.now())

    employee: Mapped["Employee"] = relationship(back_populates="wishes")






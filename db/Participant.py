from . import Base
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column
from datetime import datetime
from sqlalchemy import func, ForeignKey, BigInteger


class Participant(Base):
    __tablename__ = "participant"

    id: Mapped[int] = mapped_column(primary_key=True)
    participant_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("employee.id"))
    holiday_id: Mapped[int] = mapped_column(ForeignKey("holiday.id", ondelete="CASCADE"))
    record_time: Mapped[datetime] = mapped_column(server_default=func.now())

    employee: Mapped["Employee"] = relationship(back_populates="participants", lazy="joined")
    holiday: Mapped["Holiday"] = relationship(back_populates="participants")

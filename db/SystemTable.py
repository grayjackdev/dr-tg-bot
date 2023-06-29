from . import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class SystemTable(Base):
    __tablename__ = "system_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    call_time: Mapped[str] = mapped_column(default="12:00")
    






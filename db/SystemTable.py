from . import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class SystemTable(Base):
    __tablename__ = "system_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    call_time: Mapped[str] = mapped_column(default="12:00")
    seconds_survey: Mapped[int] = mapped_column(default=86_400)
    seconds_survey_2: Mapped[int] = mapped_column(default=14_400)
    start_interval_survey_func: Mapped[int] = mapped_column(default=60)

    






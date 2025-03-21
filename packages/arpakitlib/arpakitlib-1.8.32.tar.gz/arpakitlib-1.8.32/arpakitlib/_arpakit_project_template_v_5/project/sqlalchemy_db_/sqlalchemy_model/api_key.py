from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

import sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column

from arpakitlib.ar_datetime_util import now_utc_dt
from project.sqlalchemy_db_.sqlalchemy_model.common import SimpleDBM

if TYPE_CHECKING:
    pass


def generate_default_api_key_value() -> str:
    return (
        f"apikey"
        f"{str(uuid4()).replace('-', '')}"
        f"{str(now_utc_dt().timestamp()).replace('.', '')}"
    )


class ApiKeyDBM(SimpleDBM):
    __tablename__ = "api_key"

    title: Mapped[str | None] = mapped_column(
        sqlalchemy.TEXT,
        insert_default=None,
        nullable=True
    )
    value: Mapped[str] = mapped_column(
        sqlalchemy.TEXT,
        unique=True,
        insert_default=generate_default_api_key_value,
        server_default=sqlalchemy.func.gen_random_uuid(),
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        sqlalchemy.Boolean,
        index=True,
        insert_default=True,
        server_default="true",
        nullable=False
    )

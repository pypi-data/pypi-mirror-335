from __future__ import annotations

from typing import Any, TYPE_CHECKING

import sqlalchemy
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import mapped_column, Mapped

from arpakitlib.ar_enumeration_util import Enumeration
from project.sqlalchemy_db_.sqlalchemy_model.common import SimpleDBM

if TYPE_CHECKING:
    pass


class StoryLogDBM(SimpleDBM):
    __tablename__ = "story_log"

    class Levels(Enumeration):
        info = "info"
        warning = "warning"
        error = "error"

    class Types(Enumeration):
        error_in_execute_operation = "error_in_execute_operation"
        error_in_api = "error_in_api"
        error_in_tg_bot = "error_in_tg_bot"

    level: Mapped[str] = mapped_column(
        sqlalchemy.TEXT,
        insert_default=Levels.info,
        server_default=Levels.info,
        index=True,
        nullable=False
    )
    type: Mapped[str | None] = mapped_column(
        sqlalchemy.TEXT,
        index=True,
        insert_default=None,
        nullable=True)
    title: Mapped[str | None] = mapped_column(
        sqlalchemy.TEXT,
        insert_default=None,
        nullable=True
    )
    data: Mapped[dict[str, Any]] = mapped_column(
        postgresql.JSON,
        insert_default={},
        server_default="{}",
        nullable=False
    )

from __future__ import annotations

from typing import Any

from project.api.schema.out.admin.common import SimpleDBMAdminSO
from project.sqlalchemy_db_.sqlalchemy_model import StoryLogDBM


class StoryLogAdminSO(SimpleDBMAdminSO):
    level: str
    type: str | None
    title: str | None
    data: dict[str, Any]

    @classmethod
    def from_dbm(cls, *, simple_dbm: StoryLogDBM) -> StoryLogAdminSO:
        return cls.model_validate(simple_dbm.simple_dict_with_sd_properties())

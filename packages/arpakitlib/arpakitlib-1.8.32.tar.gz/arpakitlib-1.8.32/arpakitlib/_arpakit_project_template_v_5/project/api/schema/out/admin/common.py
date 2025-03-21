from __future__ import annotations

import datetime as dt
from typing import Any

from project.api.schema.common import BaseSO
from project.sqlalchemy_db_.sqlalchemy_model import SimpleDBM


class SimpleDBMAdminSO(BaseSO):
    id: int
    long_id: str
    slug: str | None
    creation_dt: dt.datetime
    extra_data: dict[str, Any]
    entity_name: str

    @classmethod
    def from_dbm(cls, *, simple_dbm: SimpleDBM) -> SimpleDBMAdminSO:
        return cls.model_validate(simple_dbm.simple_dict_with_sd_properties())

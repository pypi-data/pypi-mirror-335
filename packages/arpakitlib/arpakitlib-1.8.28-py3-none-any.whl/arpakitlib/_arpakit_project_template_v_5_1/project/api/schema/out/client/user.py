from __future__ import annotations

import datetime as dt
from typing import Any

from project.api.schema.out.client.common import SimpleDBMClientSO
from project.sqlalchemy_db_.sqlalchemy_model import UserDBM


class UserClientSO(SimpleDBMClientSO):
    email: str | None
    roles: list[str]
    is_active: bool
    tg_id: int | None
    tg_bot_last_action_dt: dt.datetime | None
    tg_data: dict[str, Any] | None
    roles_has_admin: bool
    roles_has_client: bool

    @classmethod
    def from_dbm(cls, *, simple_dbm: UserDBM) -> UserClientSO:
        return cls.model_validate(simple_dbm.simple_dict_with_sd_properties())

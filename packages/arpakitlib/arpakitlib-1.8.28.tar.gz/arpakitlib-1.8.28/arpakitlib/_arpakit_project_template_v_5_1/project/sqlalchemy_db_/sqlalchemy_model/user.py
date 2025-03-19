from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING, Any

import sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from arpakitlib.ar_enumeration_util import Enumeration
from arpakitlib.ar_type_util import raise_for_type
from project.sqlalchemy_db_.sqlalchemy_model.common import SimpleDBM

if TYPE_CHECKING:
    from project.sqlalchemy_db_.sqlalchemy_model.user_token import UserTokenDBM


class UserDBM(SimpleDBM):
    __tablename__ = "user"

    class Roles(Enumeration):
        admin = "admin"
        client = "client"

    email: Mapped[str | None] = mapped_column(
        sqlalchemy.TEXT,
        unique=True,
        insert_default=None,
        nullable=True
    )
    roles: Mapped[list[str]] = mapped_column(
        sqlalchemy.ARRAY(sqlalchemy.TEXT),
        insert_default=[Roles.client],
        index=True,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        sqlalchemy.Boolean,
        index=True,
        insert_default=True,
        server_default="true",
        nullable=False
    )
    tg_id: Mapped[int | None] = mapped_column(
        sqlalchemy.BIGINT,
        unique=True,
        nullable=True
    )
    tg_bot_last_action_dt: Mapped[dt.datetime | None] = mapped_column(
        sqlalchemy.TIMESTAMP(timezone=True),
        insert_default=None,
        nullable=True
    )
    tg_data: Mapped[dict[str, Any] | None] = mapped_column(
        sqlalchemy.JSON,
        insert_default={},
        server_default="{}",
        nullable=True
    )

    user_tokens: Mapped[list[UserTokenDBM]] = relationship(
        "UserTokenDBM",
        uselist=True,
        back_populates="user",
        foreign_keys="UserTokenDBM.user_id"
    )

    @property
    def roles_has_admin(self) -> bool:
        return self.Roles.admin in self.roles

    @property
    def sdp_roles_has_admin(self) -> bool:
        return self.roles_has_admin

    @property
    def roles_has_client(self) -> bool:
        return self.Roles.client in self.roles

    @property
    def sdp_roles_has_client(self) -> bool:
        return self.roles_has_client

    def compare_roles(self, roles: list[str] | str) -> bool:
        if isinstance(roles, str):
            roles = [roles]
        raise_for_type(roles, list)
        return bool(set(roles) & set(self.roles))

import logging

import fastapi
from sqladmin.authentication import AuthenticationBackend

from arpakitlib.ar_str_util import make_none_if_blank
from project.core.settings import get_cached_settings
from project.sqlalchemy_db_.sqlalchemy_db import get_cached_sqlalchemy_db
from project.sqlalchemy_db_.sqlalchemy_model import UserTokenDBM, UserDBM

SQLADMIN_AUTH_KEY = "sqladmin_auth_key"


class SQLAdminAuth(AuthenticationBackend):
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        super().__init__(secret_key=get_cached_settings().sqladmin_secret_key)

    async def login(self, request: fastapi.Request) -> bool:
        form = await request.form()

        username = form.get("username")
        if username:
            username = username.strip()
        username = make_none_if_blank(username)

        password = form.get("password")
        if password:
            password = password.strip()
        password = make_none_if_blank(password)

        if (
                get_cached_settings().sqladmin_authorize_keys is not None
                and (username is not None or password is not None)
        ):
            if (
                    (
                            is_username_correct := username in get_cached_settings().sqladmin_authorize_keys
                    )
                    or
                    (
                            is_password_correct := password in get_cached_settings().sqladmin_authorize_keys
                    )
            ):
                if is_username_correct is True:
                    request.session.update({SQLADMIN_AUTH_KEY: username})
                elif is_password_correct is True:
                    request.session.update({SQLADMIN_AUTH_KEY: password})
                return True

        if get_cached_sqlalchemy_db() is not None and (username is not None or password is not None):
            with get_cached_sqlalchemy_db().new_session() as session:
                query = session.query(UserTokenDBM)
                if username is not None:
                    query = query.filter(UserTokenDBM.value == username)
                elif password is not None:
                    query = query.filter(UserTokenDBM.value == password)
                user_token = query.one_or_none()
                if user_token is not None and user_token.user.compare_roles(UserDBM.Roles.admin):
                    request.session.update({SQLADMIN_AUTH_KEY: user_token.value})
                    return True

        return False

    async def logout(self, request: fastapi.Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: fastapi.Request) -> bool:
        sqladmin_auth_key = request.session.get(SQLADMIN_AUTH_KEY)
        if sqladmin_auth_key:
            sqladmin_auth_key = sqladmin_auth_key.strip()
        sqladmin_auth_key = make_none_if_blank(sqladmin_auth_key)

        if get_cached_settings().sqladmin_authorize_keys is not None and sqladmin_auth_key is not None:
            if sqladmin_auth_key in get_cached_settings().sqladmin_authorize_keys:
                return True

        if get_cached_sqlalchemy_db() is not None and sqladmin_auth_key is not None:
            with get_cached_sqlalchemy_db().new_session() as session:
                query = session.query(
                    UserTokenDBM
                ).filter(
                    UserTokenDBM.value == sqladmin_auth_key
                )
                user_token = query.one_or_none()
                if user_token is not None and user_token.user.compare_roles(UserDBM.Roles.admin):
                    return True

        return False

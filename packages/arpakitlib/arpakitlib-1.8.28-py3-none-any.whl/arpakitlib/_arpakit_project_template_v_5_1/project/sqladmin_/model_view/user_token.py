from project.sqladmin_.model_view.common import SimpleMV
from project.sqlalchemy_db_.sqlalchemy_model import UserTokenDBM


class UserTokenMV(SimpleMV, model=UserTokenDBM):
    name = "UserToken"
    name_plural = "UserTokens"
    column_list = [
        UserTokenDBM.id,
        UserTokenDBM.long_id,
        UserTokenDBM.slug,
        UserTokenDBM.creation_dt,
        UserTokenDBM.value,
        UserTokenDBM.user,
        UserTokenDBM.is_active,
    ]
    form_columns = [
        UserTokenDBM.slug,
        UserTokenDBM.creation_dt,
        UserTokenDBM.value,
        UserTokenDBM.user,
        UserTokenDBM.is_active,
    ]
    column_default_sort = [
        (UserTokenDBM.creation_dt, True)
    ]
    column_searchable_list = [
        UserTokenDBM.id,
        UserTokenDBM.long_id,
        UserTokenDBM.slug,
        UserTokenDBM.value,
        UserTokenDBM.user_id,
        UserTokenDBM.is_active,
    ]

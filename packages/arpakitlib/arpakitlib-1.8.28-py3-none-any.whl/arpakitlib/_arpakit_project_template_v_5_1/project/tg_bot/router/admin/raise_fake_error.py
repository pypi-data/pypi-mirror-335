import aiogram.filters

from arpakitlib.ar_aiogram_util import as_tg_command
from project.core.settings import get_cached_settings
from project.tg_bot.const import AdminTgBotCommands
from project.tg_bot.filter_.is_private_chat import IsPrivateChatTgBotFilter
from project.tg_bot.filter_.user_roles_has_admin import UserRolesHasAdminTgBotFilter
from project.tg_bot.middleware.common import MiddlewareDataTgBot

tg_bot_router = aiogram.Router()


@tg_bot_router.message(
    IsPrivateChatTgBotFilter(),
    UserRolesHasAdminTgBotFilter(),
    aiogram.filters.Command(AdminTgBotCommands.raise_fake_error)
)
@as_tg_command(passwd_validator=get_cached_settings().tg_bot_command_passwd)
async def _(
        m: aiogram.types.Message,
        middleware_data_tg_bot: MiddlewareDataTgBot,
        **kwargs
):
    raise Exception("fake error")

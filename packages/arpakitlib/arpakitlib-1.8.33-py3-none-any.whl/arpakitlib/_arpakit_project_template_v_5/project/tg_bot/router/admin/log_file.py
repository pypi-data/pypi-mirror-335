import os

import aiogram
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile

from arpakitlib.ar_aiogram_util import as_tg_command
from project.core.settings import get_cached_settings
from project.tg_bot.const import AdminTgBotCommands
from project.tg_bot.filter_.is_private_chat import IsPrivateChatTgBotFilter
from project.tg_bot.filter_.user_roles_has_admin import UserRolesHasAdminTgBotFilter

tg_bot_router = Router()


@tg_bot_router.message(
    IsPrivateChatTgBotFilter(),
    UserRolesHasAdminTgBotFilter(),
    aiogram.filters.Command(AdminTgBotCommands.log_file),
)
@as_tg_command(passwd_validator=get_cached_settings().tg_bot_command_passwd)
async def _(
        m: types.Message,
        **kwargs
):
    with open(get_cached_settings().log_filepath, mode="r") as f:
        if not f.read():
            await m.answer("log файл пустой")
            return

    await m.answer_document(
        document=FSInputFile(
            path=get_cached_settings().log_filepath,
            filename=os.path.basename(get_cached_settings().log_filepath)
        )
    )

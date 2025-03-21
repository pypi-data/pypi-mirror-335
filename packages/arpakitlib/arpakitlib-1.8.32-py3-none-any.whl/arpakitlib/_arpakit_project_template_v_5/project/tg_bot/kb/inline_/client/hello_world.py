from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from project.tg_bot.blank.client import get_cached_client_tg_bot_blank
from project.tg_bot.callback.client import HelloWorldClientCD


def hello_world_client_inline_kb_tg_bot() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    kb_builder.row(InlineKeyboardButton(
        text=get_cached_client_tg_bot_blank().but_hello_world(),
        callback_data=HelloWorldClientCD(hello_world=True).pack()
    ))

    return kb_builder.as_markup()

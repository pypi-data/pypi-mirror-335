import aiogram.filters
from aiogram.filters import or_f

from arpakitlib.ar_str_util import remove_html
from project.tg_bot.blank.client import get_cached_client_tg_bot_blank
from project.tg_bot.callback.client import HelloWorldClientCD
from project.tg_bot.const import ClientTgBotCommands
from project.tg_bot.filter_.message_text import MessageTextTgBotFilter
from project.tg_bot.kb.inline_.client.hello_world import hello_world_client_inline_kb_tg_bot
from project.tg_bot.kb.static_.client.hello_world import hello_world_client_static_kb_tg_bot
from project.tg_bot.middleware.common import MiddlewareDataTgBot

tg_bot_router = aiogram.Router()


@tg_bot_router.message(
    or_f(
        aiogram.filters.Command(ClientTgBotCommands.hello_world),
        MessageTextTgBotFilter(get_cached_client_tg_bot_blank().but_hello_world())
    ),

)
async def _(
        m: aiogram.types.Message,
        middleware_data_tg_bot: MiddlewareDataTgBot,
        **kwargs
):
    await m.answer(
        text=get_cached_client_tg_bot_blank().hello_world(),
        reply_markup=hello_world_client_inline_kb_tg_bot()
    )
    await m.answer(
        text=get_cached_client_tg_bot_blank().hello_world(),
        reply_markup=hello_world_client_static_kb_tg_bot()
    )


@tg_bot_router.callback_query(
    HelloWorldClientCD.filter()
)
async def _(
        cq: aiogram.types.CallbackQuery,
        middleware_data_tg_bot: MiddlewareDataTgBot,
        **kwargs
):
    await cq.message.delete_reply_markup()
    await cq.message.answer(text=remove_html(get_cached_client_tg_bot_blank().hello_world()))

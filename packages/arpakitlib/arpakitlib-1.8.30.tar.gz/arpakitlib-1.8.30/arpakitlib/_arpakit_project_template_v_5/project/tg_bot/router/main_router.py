from aiogram import Router

from project.tg_bot.router.admin import reinit_sqlalchemy_db, arpakitlib_project_template_info, raise_fake_error, me, \
    log_file, clear_log_file, set_tg_bot_commands, init_sqlalchemy_db, drop_sqlalchemy_db, kb_with_remove_message, \
    kb_with_old_cd, kb_with_raise_error, kb_with_not_modified
from project.tg_bot.router.general import remove_message, start, about, healthcheck, hello_world, \
    support, error_handler, raw_callback_query, raw_message, raw_inline_query, author

main_tg_bot_router = Router()

# admin
main_tg_bot_router.include_router(router=reinit_sqlalchemy_db.tg_bot_router)
main_tg_bot_router.include_router(router=arpakitlib_project_template_info.tg_bot_router)
main_tg_bot_router.include_router(router=raise_fake_error.tg_bot_router)
main_tg_bot_router.include_router(router=me.tg_bot_router)
main_tg_bot_router.include_router(router=log_file.tg_bot_router)
main_tg_bot_router.include_router(router=clear_log_file.tg_bot_router)
main_tg_bot_router.include_router(router=set_tg_bot_commands.tg_bot_router)
main_tg_bot_router.include_router(router=init_sqlalchemy_db.tg_bot_router)
main_tg_bot_router.include_router(router=drop_sqlalchemy_db.tg_bot_router)
main_tg_bot_router.include_router(router=kb_with_remove_message.tg_bot_router)
main_tg_bot_router.include_router(router=kb_with_old_cd.tg_bot_router)
main_tg_bot_router.include_router(router=kb_with_raise_error.tg_bot_router)
main_tg_bot_router.include_router(router=kb_with_not_modified.tg_bot_router)

# general
main_tg_bot_router.include_router(router=error_handler.tg_bot_router)
main_tg_bot_router.include_router(router=remove_message.tg_bot_router)
main_tg_bot_router.include_router(router=start.tg_bot_router)
main_tg_bot_router.include_router(router=about.tg_bot_router)
main_tg_bot_router.include_router(router=healthcheck.tg_bot_router)
main_tg_bot_router.include_router(router=hello_world.tg_bot_router)
main_tg_bot_router.include_router(router=support.tg_bot_router)
main_tg_bot_router.include_router(router=author.tg_bot_router)
main_tg_bot_router.include_router(router=raw_message.tg_bot_router)
main_tg_bot_router.include_router(router=raw_inline_query.tg_bot_router)
main_tg_bot_router.include_router(router=raw_callback_query.tg_bot_router)

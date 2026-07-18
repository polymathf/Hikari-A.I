from aiogram import Router
from handlers import start
from handlers import lang
from handlers import group_me
from handlers import admin
from handlers import admin_broadcast
from handlers import admin_cancel
from handlers import broadcast
from handlers import group_messages

from handlers import digest_handler
from handlers import gender
from handlers import lang_handler
from handlers import style_handler

def get_routers() -> list[Router]:
    return [
        admin.router,
        broadcast.router,
        start.router,
        lang.router,
        group_me.router,
        admin_broadcast.router,
        admin_cancel.router,
        digest_handler.router,
        gender.router,
        lang_handler.router,
        style_handler.router,
        group_messages.router
    ]
from aiogram import Router, types, F
from datetime import datetime
from db.json_storage import save_message_entry
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner
from db.group import add_group, get_group_lang

router = Router()

@router.message(F.chat.type.in_({"group", "supergroup"}))
async def handle_group_message(message: types.Message, bot):
    if not message.text:
        return

    user = message.from_user
    chat_id = message.chat.id

    group_lang = await get_group_lang(chat_id)
    if group_lang is None:
        await add_group(chat_id=chat_id, lang="eng", active=True, add_time=datetime.now().timestamp(), style="default")

    try:
        member = await bot.get_chat_member(chat_id, user.id)
        is_admin = isinstance(member, (ChatMemberAdministrator, ChatMemberOwner))
    except:
        is_admin = False

    reply_data = None
    if message.reply_to_message:
        replied_user = message.reply_to_message.from_user
        reply_data = {
            "full_name": replied_user.full_name,
            "username": replied_user.username,
            "content": message.reply_to_message.text or ""
        }

    entry = {
        "chat_id": chat_id,
        "user_id": user.id,
        "full_name": user.full_name,
        "username": user.username,
        "gender": None,
        "is_admin": is_admin,
        "timestamp": message.date.strftime("%d.%m.%Y %H:%M"),
        "content": message.text,
        "reply_to": reply_data
    }

    save_message_entry(entry)
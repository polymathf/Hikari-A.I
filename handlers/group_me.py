from aiogram import types, Router
from aiogram.enums import ChatType, ChatMemberStatus
import time

from db.user import get_user_lang
from db.group import add_group, deactivate_group  
from utils.lang import t
from utils.escape_html import escape_html

router = Router()

@router.my_chat_member()
async def group_me_welcome(event: types.ChatMemberUpdated):
    try:
        if event.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            return

        chat_id = event.chat.id
        user_id = event.from_user.id
        new_status = event.new_chat_member.status

        if new_status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR]:
            lang = await get_user_lang(user_id) or "eng"
            await add_group(chat_id, lang, active=True, style="default")
            
            await event.bot.send_message(
                chat_id=chat_id,
                text=t(escape_html("group_me_welcome"), lang,
                     first_name=event.from_user.first_name, user_id=user_id),
                disable_notification=True
            )

        elif new_status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
            await deactivate_group(chat_id)

    except Exception as e:
        print(f"[group_me_welcome] error {e}")

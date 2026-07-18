from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ChatType

from db.user import add_user
from utils.lang import t

router = Router()

@router.message(F.chat.type == ChatType.PRIVATE)
async def private_message_handler(message: types.Message):
    try:
        user_id = message.from_user.id
        await add_user(user_id)

        kb = InlineKeyboardBuilder()
        kb.button(text="🇰🇿 Kazakh", callback_data="lang_kaz")
        kb.button(text="🇷🇺 Русский", callback_data="lang_rus")
        kb.button(text="🇬🇧 English", callback_data="lang_eng")
        kb.button(text="🇨🇳 中文", callback_data="lang_chi")
        kb.button(text="🇺🇦 Українська", callback_data="lang_ukr")
        kb.adjust(2, 2)

        await message.answer(
            t("start", "eng"),
            reply_markup=kb.as_markup()
        )
    except Exception as e:
        print(f"[private_message_handler error] {e}")
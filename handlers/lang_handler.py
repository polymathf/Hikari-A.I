from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ChatMemberStatus
from utils.lang import t
from db.group import get_group_lang

router = Router()

@router.message(Command("lang"))
async def change_lang_command(message: types.Message):
    lang = await get_group_lang(message.chat.id) or "eng"
    
    member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        return
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🇰🇿 Kazakh", callback_data="langg_kaz")
    kb.button(text="🇷🇺 Русский", callback_data="langg_rus")
    kb.button(text="🇬🇧 English", callback_data="langg_eng")
    kb.button(text="🇨🇳 中文", callback_data="langg_chi")
    kb.button(text="🇺🇦 Українська", callback_data="langg_ukr")
    kb.adjust(2, 2)
    
    await message.reply(t("lang_change_prompt", lang), reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("langg_"))
async def set_lang_callback(callback: types.CallbackQuery):
    member = await callback.bot.get_chat_member(callback.message.chat.id, callback.from_user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        return
    
    lang_code = callback.data.split("_")[1]
    chat_id = callback.message.chat.id
    
    from db.group import add_group
    await add_group(chat_id, lang_code)
    
    await callback.message.edit_text(
        t("lang_change_success", lang_code),
        reply_markup=None
    )
    await callback.answer()
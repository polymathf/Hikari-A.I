from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.lang import t
from config import PROMPT_STYLES
from db.group import get_group_lang, get_group_style, set_group_style

router = Router()

async def get_style_keyboard(chat_id: int, lang: str = "eng"):
    current_style = await get_group_style(chat_id) or "default"
    keyboard = []
    
    for style_id in PROMPT_STYLES.keys():
        is_current = "✅ " if style_id == current_style else ""
        style_name = t(f"style_{style_id}", lang)
        text = f"{is_current}{style_name}"
        keyboard.append([InlineKeyboardButton(
            text=text,
            callback_data=f"set_style:{style_id}"
        )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.message(Command("style"))
async def style_command(message: types.Message):
    member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
    if not member.status in ['administrator', 'creator']:
        await message.reply(t("only_admins", await get_group_lang(message.chat.id)))
        return
    
    lang = await get_group_lang(message.chat.id) or "eng"
    keyboard = await get_style_keyboard(message.chat.id, lang)
    
    await message.reply(
        t("select_style", lang),
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("set_style:"))
async def set_style_callback(callback: types.CallbackQuery):
    try:
        member = await callback.bot.get_chat_member(callback.message.chat.id, callback.from_user.id)
        if not member.status in ['administrator', 'creator']:
            return
        
        style_id = callback.data.split(":")[1]
        
        await set_group_style(callback.message.chat.id, style_id)
        lang = await get_group_lang(callback.message.chat.id) or "eng"
        
        keyboard = await get_style_keyboard(callback.message.chat.id, lang)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        style_name = t(f"style_{style_id}", lang)
        await callback.answer(t("style_changed", lang).format(style=style_name))
    except Exception:
        pass
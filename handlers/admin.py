from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from utils.lang import t
from db.user import get_user_lang, count_users
from db.group import count_groups, count_active_groups

router = Router()

async def send_admin_panel(message_or_callback, user_id: int, state: FSMContext):
    await state.clear()

    lang = await get_user_lang(user_id) or "eng"

    users_count = await count_users()
    total_groups = await count_groups()
    active_groups = await count_active_groups()
    inactive_groups = total_groups - active_groups

    kb = InlineKeyboardBuilder()
    kb.button(text=t("admin_broadcast_button", lang), callback_data="broadcast")
    kb.adjust(1)

    text = t("admin_panel", lang) + "\n\n" + t("admin_stats", lang).format(
        users=users_count,
        active_groups=active_groups,
        inactive_groups=inactive_groups,
        total_groups=total_groups
    )

    if isinstance(message_or_callback, types.CallbackQuery):
        message = message_or_callback.message
    else:
        message = message_or_callback

    try:
        await message.edit_text(text, reply_markup=kb.as_markup())
    except:
        await message.answer(text, reply_markup=kb.as_markup())

@router.message(Command("admin"), F.chat.type == ChatType.PRIVATE)
async def admin_command(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await send_admin_panel(message, message.from_user.id, state)


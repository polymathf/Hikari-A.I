from aiogram import Router, types
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.lang import t
from db.user import get_user_lang

router = Router()

@router.callback_query(F.data == "broadcast")
async def show_broadcast_targets(callback: types.CallbackQuery):
    lang = await get_user_lang(callback.from_user.id) or "eng"

    kb = InlineKeyboardBuilder()
    kb.button(text=t("broadcast_users", lang), callback_data="broadcast_users")
    kb.button(text=t("broadcast_groups", lang), callback_data="broadcast_groups")
    kb.button(text=t("cancel", lang), callback_data="cancel_broadcast")
    kb.adjust(2, 1)

    await callback.message.edit_text(
        t("broadcast_choose_target", lang),
        reply_markup=kb.as_markup()
    )
    await callback.answer()

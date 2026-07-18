from aiogram import Router, types
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from utils.lang import t
from handlers.admin import send_admin_panel

router = Router()

@router.callback_query(F.data == "cancel_broadcast")
async def cancel_broadcast(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    preview_id = data.get("preview_message_id")
    if preview_id:
        try:
            await callback.bot.delete_message(callback.message.chat.id, preview_id)
        except:
            pass

    await send_admin_panel(callback.message, callback.from_user.id, state)
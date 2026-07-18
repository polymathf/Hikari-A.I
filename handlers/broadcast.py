from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from asyncio import sleep

from db.user import get_all_users, get_user_lang
from utils.lang import t
from db.group import get_active_groups

router = Router()

class Broadcast(StatesGroup):
    waiting_for_content = State()
    waiting_for_confirmation = State()

async def broadcast_to_targets(
    message: types.Message,
    targets: list[int],
    callback_msg: types.Message,
    lang: str
):
    success = 0
    failed = 0

    for target_id in targets:
        try:
            await message.copy_to(chat_id=target_id)
            success += 1
        except:
            failed += 1
        await sleep(0.7)

    text = t("broadcast_done", lang).format(success=success, failed=failed)

    try:
        await callback_msg.edit_text(text)
    except:
        await callback_msg.answer(text)

@router.callback_query(F.data == "broadcast_users")
async def ask_broadcast_groups_content(callback: types.CallbackQuery, state: FSMContext):
    lang = await get_user_lang(callback.from_user.id) or "eng"
    kb = InlineKeyboardBuilder()
    kb.button(text=t("cancel", lang), callback_data="cancel_broadcast")
    msg = await callback.message.edit_text(t("broadcast_ask_content", lang), reply_markup=kb.as_markup())
    await state.set_state(Broadcast.waiting_for_content)
    await state.update_data(target="users", cancel_message_id=msg.message_id)
    await callback.answer()

@router.message(Broadcast.waiting_for_content)
async def receive_broadcast_content(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(content=message)
    lang = await get_user_lang(message.from_user.id) or "eng"

    if "cancel_message_id" in data:
        try:
            await message.bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=data["cancel_message_id"],
                reply_markup=None
            )
        except Exception as e:
            print(f"Couldn't remove buttons: {e}")

    kb = InlineKeyboardBuilder()
    kb.button(text=t("confirm", lang), callback_data="confirm_broadcast")
    kb.button(text=t("cancel", lang), callback_data="cancel_broadcast")
    kb.adjust(2)

    preview = await message.copy_to(
        chat_id=message.chat.id,
        reply_markup=kb.as_markup()
    )

    await state.update_data(preview_message_id=preview.message_id)
    await state.set_state(Broadcast.waiting_for_confirmation)


@router.callback_query(F.data == "broadcast_groups")
async def ask_broadcast_groups_content(callback: types.CallbackQuery, state: FSMContext):
    lang = await get_user_lang(callback.from_user.id) or "eng"
    kb = InlineKeyboardBuilder()
    kb.button(text=t("cancel", lang), callback_data="cancel_broadcast")
    msg = await callback.message.edit_text(
        t("broadcast_ask_content", lang),
        reply_markup=kb.as_markup()
    )
    await state.set_state(Broadcast.waiting_for_content)
    await state.update_data(
        target="groups",
        cancel_message_id=msg.message_id
    )
    await callback.answer()

@router.callback_query(F.data == "confirm_broadcast")
async def confirm_broadcast(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except:
        pass

    data = await state.get_data()
    message: types.Message = data.get("content")
    target = data.get("target", "users")
    lang = await get_user_lang(callback.from_user.id) or "eng"

    if target == "groups":
        ids = await get_active_groups()
    else:
        ids = await get_all_users()

    await broadcast_to_targets(message, ids, callback.message, lang)
    await state.clear()

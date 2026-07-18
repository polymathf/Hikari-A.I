from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from db.json_storage import update_user_gender
from db.group import get_group_lang
from utils.lang import t

router = Router()

GENDER_CHOICES = ["auto", "male", "female"]

@router.message(Command("gender"))
async def gender_command(message: types.Message):
    lang = await get_group_lang(message.chat.id) or "eng"
    user_id = message.from_user.id

    gender = "auto"

    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=t(f"gender_{GENDER_CHOICES[0]}", lang), callback_data=f"gender:{GENDER_CHOICES[0]}")],
            [
                types.InlineKeyboardButton(text=t(f"gender_{g}", lang), callback_data=f"gender:{g}")
                for g in GENDER_CHOICES[1:]
            ]
        ]
    )

    await message.answer(
        t("gender_current", lang, gender=t(f"gender_{gender}", lang)),
        reply_markup=kb
    )


@router.callback_query(lambda q: q.data.startswith("gender:"))
async def gender_callback(query: CallbackQuery):
    try:
        gender_value = query.data.split(":")[1]
        user_id = query.from_user.id
        lang = await get_group_lang(query.message.chat.id) or "eng"

        update_user_gender(user_id, gender_value)

        await query.message.edit_text(
            t("gender_current", lang, gender=t(f"gender_{gender_value}", lang)),
            reply_markup=query.message.reply_markup
        )
        await query.answer("✅")
    except Exception:
        pass
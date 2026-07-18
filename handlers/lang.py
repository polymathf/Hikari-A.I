from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot
from db.user import set_user_lang
from utils.lang import t

router = Router()

@router.callback_query(F.data.startswith("lang_"))
async def language_selected(callback: types.CallbackQuery, bot: Bot):
    try:
        user_id = callback.from_user.id
        lang = callback.data.split("_")[1]
        await set_user_lang(user_id, lang)

        bot_info = await bot.get_me()
        username = bot_info.username

        kb = InlineKeyboardBuilder()
        kb.button(
            text=t("kb_add_to_group", lang),
            url=f"https://t.me/{username}?startgroup=true"
        )

        await callback.message.edit_text(
            t("welcome", lang),
            reply_markup=kb.as_markup()
        )
        await callback.answer(t("language_selected", lang))

    except Exception as e:
        print(f"[language_selected error]: {e}")
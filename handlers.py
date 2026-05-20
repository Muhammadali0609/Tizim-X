from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db import save_user_language
from texts import TEXTS


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇺🇿 O‘zbekcha", callback_data="lang_uz"),
        ]
    ]

    await update.message.reply_text(
        TEXTS["ru"]["choose_language"],
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = query.data.replace("lang_", "")
    save_user_language(user_id, lang)

    await query.edit_message_text(
        TEXTS[lang]["language_saved"] + "\n\n" + TEXTS[lang]["start"]
    )

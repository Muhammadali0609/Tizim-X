from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatMemberStatus
from telegram.ext import ContextTypes
from db import save_user_language, save_group, get_group_settings, get_group_language, save_group_language
from texts import TEXTS
from filters import has_link, has_bad_word
from admins import is_admin
import asyncio

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

async def bot_added_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.my_chat_member

    if not message:
        return

    new_status = message.new_chat_member.status

    if new_status not in [
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
    ]:
        return

    chat = message.chat
    save_group(chat.id, chat.title)

    bot_member = await chat.get_member(context.bot.id)

    has_admin = bot_member.status == ChatMemberStatus.ADMINISTRATOR
    lang = get_group_language(chat.id)
    text = TEXTS[lang]["group_connected"]

    if not has_admin:
        text += "\n\n" + TEXTS["ru"]["no_admin_rights"]

    await context.bot.send_message(
        chat_id=chat.id,
        text=text
    )

async def check_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or not message.text:
        return

    if message.chat.type not in ["group", "supergroup"]:
        return

    save_group(message.chat.id, message.chat.title)

    settings = get_group_settings(message.chat.id)
    
    user = message.from_user

    if await is_admin(message.chat, user.id):
        return
    
    text = message.text

    if settings["anti_links"] and has_link(text):
        try:
            await message.delete()
        except Exception as e:
            print("DELETE LINK ERROR:", e)
        return
    
    if settings["anti_bad_words"] and has_bad_word(text):
        try:
            await message.delete()
        except Exception as e:
            print("DELETE BAD WORD ERROR:", e)
        return

async def set_group_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or message.chat.type not in ["group", "supergroup"]:
        return

    try:
        await message.delete()
    except Exception as e:
        print("DELETE COMMAND ERROR:", e)

    user = message.from_user

    if not await is_admin(message.chat, user.id):
        return

    command = message.text.split()[0].lower()

    if command.startswith("/ru"):
        lang = "ru"
        text_key = "group_language_ru"
    elif command.startswith("/uz"):
        lang = "uz"
        text_key = "group_language_uz"
    else:
        return

    save_group(message.chat.id, message.chat.title)
    save_group_language(message.chat.id, lang)

    msg = await message.chat.send_message(
        TEXTS[lang][text_key]
    )
    
    await asyncio.sleep(2)
    
    try:
        await msg.delete()
    except Exception as e:
        print("DELETE TEMP MESSAGE ERROR:", e)

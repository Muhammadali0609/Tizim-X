from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions, ReplyKeyboardMarkup
from telegram.constants import ChatMemberStatus
from telegram.ext import ContextTypes
from db import save_user_language, get_user_language, save_group, get_group_settings, get_group_language, save_group_language, get_required_channel, save_group_admin, get_user_groups
from texts import TEXTS
from filters import has_link, has_bad_word
from admins import is_admin
import asyncio

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang_keyboard = [
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇺🇿 O‘zbekcha", callback_data="lang_uz"),
        ]
    ]

    await update.message.reply_text(
        TEXTS["ru"]["choose_language"],
        reply_markup=InlineKeyboardMarkup(lang_keyboard)
    )
    
async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    lang = query.data.replace("lang_", "")
    user_id = query.from_user.id

    save_user_language(user_id, lang)

    keyboard_text = (
        "⚙️ Настройки"
        if lang == "ru"
        else "⚙️ Sozlamalar"
    )

    keyboard = ReplyKeyboardMarkup(
        [[keyboard_text]],
        resize_keyboard=True
    )

    await query.answer(TEXTS[lang]["language_saved"])

    await query.message.reply_text(
        TEXTS[lang]["start"],
        reply_markup=keyboard
    )

    try:
        await query.message.delete()
    except Exception as e:
        print("DELETE LANGUAGE MESSAGE ERROR:", e)

async def settings_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = update.effective_user.id

    lang = get_user_language(user_id)
    groups = get_user_groups(user_id)

    if not groups:
        await message.reply_text(TEXTS[lang]["no_groups"])
        return

    keyboard = []

    for chat_id, title in groups:
        keyboard.append([
            InlineKeyboardButton(
                title,
                callback_data=f"group_settings:{chat_id}"
            )
        ])

    await message.reply_text(
        TEXTS[lang]["choose_group"],
        reply_markup=InlineKeyboardMarkup(keyboard)
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

    save_group_admin(message.chat.id, user.id)

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

async def new_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or not message.new_chat_members:
        return

    if message.chat.type not in ["group", "supergroup"]:
        return

    required_channel, force_subscribe = get_required_channel(message.chat.id)

    if not force_subscribe or not required_channel:
        return

    for user in message.new_chat_members:
        if user.is_bot:
            continue

        try:
            await message.chat.restrict_member(
                user_id=user.id,
                permissions=ChatPermissions(
                    can_send_messages=False
                )
            )

            keyboard = [
                [
                    InlineKeyboardButton(
                        "📢 Подписаться",
                        url=f"https://t.me/{required_channel.replace('@', '')}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "✅ Проверить",
                        callback_data=f"check_sub:{message.chat.id}:{user.id}"
                    )
                ]
            ]

            await message.chat.send_message(
                f"{user.first_name}, чтобы писать в группе, подпишитесь на канал.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        except Exception as e:
            print("FORCE SUBSCRIBE ERROR:", e)

    try:
        await message.delete()
    except Exception as e:
        print("DELETE JOIN MESSAGE ERROR:", e)

async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    data = query.data.split(":")
    chat_id = int(data[1])
    target_user_id = int(data[2])

    if query.from_user.id != target_user_id:
        await query.answer("Bu tugma siz uchun emas", show_alert=True)
        return

    required_channel, force_subscribe = get_required_channel(chat_id)

    if not force_subscribe or not required_channel:
        await query.answer("Sozlama topilmadi", show_alert=True)
        return

    channel_username = required_channel.replace("@", "")

    try:
        member = await context.bot.get_chat_member(
            chat_id=f"@{channel_username}",
            user_id=target_user_id
        )

        if member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
        ]:
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=target_user_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_audios=True,
                    can_send_documents=True,
                    can_send_photos=True,
                    can_send_videos=True,
                    can_send_video_notes=True,
                    can_send_voice_notes=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_invite_users=True,
                )
            )

            await query.answer("✅ Obuna tasdiqlandi", show_alert=True)

            try:
                await query.message.delete()
            except Exception as e:
                print("DELETE SUB MESSAGE ERROR:", e)

        else:
            await query.answer("❌ Avval kanalga obuna bo‘ling", show_alert=True)

    except Exception as e:
        print("CHECK SUB ERROR:", e)
        await query.answer("❌ Obunani tekshirib bo‘lmadi", show_alert=True)

async def clean_service_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message:
        return

    if message.chat.type not in ["group", "supergroup"]:
        return

    settings = get_group_settings(message.chat.id)

    if not settings["clean_service_messages"]:
        return

    try:
        await message.delete()
    except Exception as e:
        print("DELETE SERVICE MESSAGE ERROR:", e)

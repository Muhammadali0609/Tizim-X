from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions, ReplyKeyboardMarkup
from telegram.constants import ChatMemberStatus
from telegram.ext import ContextTypes
from datetime import datetime, timedelta, timezone
from db import(save_user_language,
    get_user_language,
    save_group,
    get_group_settings,
    get_group_language,
    save_group_language,
    get_required_channel,
    save_group_admin,
    get_user_groups,
    get_bad_words_page,
    get_bad_words_count,
    add_bad_words,
    get_bad_words_for_check,
    set_group_setting,
    get_ad_links,
    add_ad_links,
    find_bad_word,
    delete_bad_word,
    get_ad_phrases,
    add_ad_phrases,
    get_ad_phrases_for_check,
    get_ad_links_for_check,
    delete_ad_link_by_index,
    delete_ad_phrase_by_index,
    get_ad_exceptions,
    add_ad_exceptions,
    delete_ad_exception_by_index,
    get_ad_exceptions_for_check,
    set_group_number_setting,
    add_warning,
    reset_warnings
)
from texts import TEXTS
from filters import has_link, has_bad_word, has_ad_phrase, has_custom_ad_link, has_ad_exception
from admins import is_admin
import asyncio
import math
import re

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
        TEXTS[lang]["manage_button"]
    )
    
    language_text = (
        TEXTS[lang]["language_button"]
    )

    keyboard = ReplyKeyboardMarkup(
        [[keyboard_text, language_text]],
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

    valid_groups = []

    for chat_id, title in groups:
        try:
            chat = await context.bot.get_chat(chat_id)

            if not await is_admin(chat, user_id):
                continue
    
            valid_groups.append((chat_id, title))

        except Exception as e:
            print("CHECK USER GROUP ACCESS ERROR:", e)

    if not valid_groups:
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
    from db import seed_default_bad_words
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
    seed_default_bad_words(chat.id)

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
    lang = get_group_language(message.chat.id)
    user = message.from_user

    if await is_admin(message.chat, user.id):
        return
    
    text = message.text

    ad_exceptions = get_ad_exceptions_for_check(message.chat.id)

    if has_ad_exception(text, ad_exceptions):
        return
    
    if settings["anti_links"] and has_link(text):
        try:
            await message.delete()
    
            await handle_warning(
                message=message,
                lang=lang,
                reason="ads",
                reason_key="reason_ads",
                limit=settings["ads_warn_limit"],
                punish_enabled=settings["punish_ads"],
                show_warning=settings["warn_ads"],
            )
    
        except Exception as e:
            print("DELETE LINK ERROR:", e)
    
        return

    custom_links = get_ad_links_for_check(message.chat.id)

    if has_custom_ad_link(text, custom_links):
        try:
            await message.delete()
    
            await handle_warning(
                message=message,
                lang=lang,
                reason="ads",
                reason_key="reason_ads",
                limit=settings["ads_warn_limit"],
                punish_enabled=settings["punish_ads"],
                show_warning=settings["warn_ads"],
            )
    
        except Exception as e:
            print("DELETE CUSTOM AD LINK ERROR:", e)
    
        return

    ad_phrases = get_ad_phrases_for_check(message.chat.id)

    if has_ad_phrase(text, ad_phrases):
        try:
            await message.delete()
    
            await handle_warning(
                message=message,
                lang=lang,
                reason="ads",
                reason_key="reason_ads",
                limit=settings["ads_warn_limit"],
                punish_enabled=settings["punish_ads"],
                show_warning=settings["warn_ads"],
            )
    
        except Exception as e:
            print("DELETE AD PHRASE ERROR:", e)
    
        return
    
    if settings["anti_bad_words"]:
        bad_words = get_bad_words_for_check(message.chat.id)
    
        if has_bad_word(text, bad_words):
            try:
                await message.delete()
    
                await handle_warning(
                    message=message,
                    lang=lang,
                    reason="bad_words",
                    reason_key="reason_bad_word",
                    limit=settings["bad_words_warn_limit"],
                    punish_enabled=settings["punish_bad_words"],
                    show_warning=settings["warn_bad_words"],
                )
    
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

async def group_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    chat_id = int(query.data.split(":")[1])

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("GROUP SETTINGS ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    keyboard = [
        [
            InlineKeyboardButton(TEXTS[lang]["btn_bad_words"], callback_data=f"bad_words_panel:{chat_id}:0"),
            InlineKeyboardButton(TEXTS[lang]["btn_ads"], callback_data=f"ads_panel:{chat_id}"),
        ],
        [
            InlineKeyboardButton(TEXTS[lang]["btn_warnings"], callback_data=f"warnings_panel:{chat_id}"),
            InlineKeyboardButton(TEXTS[lang]["btn_restrictions"], callback_data=f"panel:restrictions:{chat_id}"),
        ],
        [
            InlineKeyboardButton(TEXTS[lang]["btn_settings"], callback_data=f"panel:settings:{chat_id}"),
        ],
        [
            InlineKeyboardButton(TEXTS[lang]["btn_transfer_settings"], callback_data=f"panel:transfer:{chat_id}"),
        ],
        [
            InlineKeyboardButton(TEXTS[lang]["back_button"], callback_data="back_groups")
        ],
    ]

    await query.edit_message_text(
        TEXTS[lang]["group_panel"].format(title=chat.title),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def back_groups_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    lang = get_user_language(user_id)

    groups = get_user_groups(user_id)

    keyboard = []

    for chat_id, title in groups:
        keyboard.append([
            InlineKeyboardButton(
                title,
                callback_data=f"group_settings:{chat_id}"
            )
        ])

    await query.edit_message_text(
        TEXTS[lang]["choose_group"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def build_bad_words_keyboard(lang: str, chat_id: int, page: int, total_pages: int):
    nav_buttons = []

    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                TEXTS[lang]["btn_prev"],
                callback_data=f"bad_words_page:{chat_id}:{page - 1}"
            )
        )

    nav_buttons.append(
        InlineKeyboardButton(
            TEXTS[lang]["btn_search"],
            callback_data=f"bad_words_search:{chat_id}"
        )
    )

    if page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton(
                TEXTS[lang]["btn_next"],
                callback_data=f"bad_words_page:{chat_id}:{page + 1}"
            )
        )

    keyboard = []

    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([
        InlineKeyboardButton(
            TEXTS[lang]["btn_add_bad_word"],
            callback_data=f"bad_words_add:{chat_id}"
        )
    ])
    
    keyboard.append([
        InlineKeyboardButton(
            TEXTS[lang]["btn_back_panel"],
            callback_data=f"group_settings:{chat_id}"
        )
    ])

    return InlineKeyboardMarkup(keyboard)

async def bad_words_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    data = query.data.split(":")
    chat_id = int(data[1])
    page = int(data[2]) if len(data) > 2 else 0

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("BAD WORDS ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    total_count = get_bad_words_count(chat_id)

    if total_count == 0:
        await query.edit_message_text(
            TEXTS[lang]["bad_words_empty"],
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        TEXTS[lang]["btn_search"],
                        callback_data=f"bad_words_search:{chat_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        TEXTS[lang]["btn_back_panel"],
                        callback_data=f"group_settings:{chat_id}"
                    )
                ]
            ])
        )
        return

    total_pages = math.ceil(total_count / 30)
    rows = get_bad_words_page(chat_id, page)

    words_text = "\n".join(
        f"{i + 1 + page * 30}. {word}"
        for i, (_, word) in enumerate(rows)
    )

    await query.edit_message_text(
        TEXTS[lang]["bad_words_title"].format(
            words=words_text,
            page=page + 1,
            total_pages=total_pages
        ),
        reply_markup=build_bad_words_keyboard(
            lang=lang,
            chat_id=chat_id,
            page=page,
            total_pages=total_pages
        )
    )

async def add_bad_word_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    chat_id = int(query.data.split(":")[1])

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("ADD BAD WORD ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    context.user_data["state"] = "adding_bad_words"
    context.user_data["target_chat_id"] = chat_id

    await query.message.reply_text(TEXTS[lang]["add_bad_word_prompt"])

async def private_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or message.chat.type != "private":
        return

    user_id = update.effective_user.id
    lang = get_user_language(user_id)

    if context.user_data.get("state") == "adding_ad_exception":
        chat_id = context.user_data.get("target_chat_id")
    
        exception = message.text.strip().lower()
    
        if exception:
            add_ad_exceptions(chat_id, [exception])
    
        context.user_data.clear()
    
        await message.reply_text(TEXTS[lang]["ad_exception_added"])
        return
    
    
    if context.user_data.get("state") == "deleting_ad_exception":
        chat_id = context.user_data.get("target_chat_id")
    
        text = message.text.strip().split()[0]
    
        if not text.isdigit():
            await message.reply_text(TEXTS[lang]["ad_exception_not_found"])
            context.user_data.clear()
            return
    
        deleted = delete_ad_exception_by_index(chat_id, int(text))
    
        context.user_data.clear()
    
        await message.reply_text(
            TEXTS[lang]["ad_exception_deleted"]
            if deleted
            else TEXTS[lang]["ad_exception_not_found"]
        )
        return
    
    if context.user_data.get("state") == "deleting_ad_link":
        chat_id = context.user_data.get("target_chat_id")
    
        text = message.text.strip().split()[0]
    
        if not text.isdigit():
            await message.reply_text(TEXTS[lang]["ad_link_not_found"])
            context.user_data.clear()
            return
    
        deleted = delete_ad_link_by_index(chat_id, int(text))
    
        context.user_data.clear()
    
        await message.reply_text(
            TEXTS[lang]["ad_link_deleted"]
            if deleted
            else TEXTS[lang]["ad_link_not_found"]
        )
        return
    
    
    if context.user_data.get("state") == "deleting_ad_phrase":
        chat_id = context.user_data.get("target_chat_id")
    
        text = message.text.strip().split()[0]
    
        if not text.isdigit():
            await message.reply_text(TEXTS[lang]["ad_phrase_not_found"])
            context.user_data.clear()
            return
    
        deleted = delete_ad_phrase_by_index(chat_id, int(text))
    
        context.user_data.clear()
    
        await message.reply_text(
            TEXTS[lang]["ad_phrase_deleted"]
            if deleted
            else TEXTS[lang]["ad_phrase_not_found"]
        )
        return
    
    if context.user_data.get("state") == "adding_ad_links":
        chat_id = context.user_data.get("target_chat_id")

        try:
            chat = await context.bot.get_chat(chat_id)

            if not await is_admin(chat, user_id):
                await message.reply_text(TEXTS[lang]["access_denied"])
                context.user_data.clear()
                return

        except Exception as e:
            print("ADD AD LINK TEXT ACCESS ERROR:", e)
            await message.reply_text(TEXTS[lang]["access_denied"])
            context.user_data.clear()
            return

        link = message.text.strip().lower()

        if link:
            add_ad_links(chat_id, [link])

        context.user_data.clear()

        await message.reply_text(TEXTS[lang]["ad_links_added"])
        return

    if context.user_data.get("state") == "searching_bad_word":
        chat_id = context.user_data.get("target_chat_id")
    
        try:
            chat = await context.bot.get_chat(chat_id)
    
            if not await is_admin(chat, user_id):
                await message.reply_text(TEXTS[lang]["access_denied"])
                context.user_data.clear()
                return
    
        except Exception as e:
            print("SEARCH BAD WORD ACCESS ERROR:", e)
            await message.reply_text(TEXTS[lang]["access_denied"])
            context.user_data.clear()
            return
    
        query_text = message.text.strip()
    
        result = find_bad_word(chat_id, query_text)
    
        context.user_data.clear()
    
        if not result:
            await message.reply_text(TEXTS[lang]["bad_word_not_found"])
            return
    
        await message.reply_text(
            TEXTS[lang]["bad_word_found"].format(
                index=result["index"],
                word=result["word"]
            ),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        TEXTS[lang]["btn_delete"],
                        callback_data=f"delete_bad_word:{chat_id}:{result['id']}"
                    )
                ]
            ])
        )
        return
    
    if context.user_data.get("state") == "adding_bad_words":
        chat_id = context.user_data.get("target_chat_id")

        try:
            chat = await context.bot.get_chat(chat_id)

            if not await is_admin(chat, user_id):
                await message.reply_text(TEXTS[lang]["access_denied"])
                context.user_data.clear()
                return

        except Exception as e:
            print("ADD BAD WORD TEXT ACCESS ERROR:", e)
            await message.reply_text(TEXTS[lang]["access_denied"])
            context.user_data.clear()
            return

        raw_text = message.text.strip().lower()

        words = re.findall(r"[^\s,;]+", raw_text)

        words = list(dict.fromkeys(words))

        if words:
            add_bad_words(chat_id, words)

        context.user_data.clear()

        await message.reply_text(TEXTS[lang]["bad_words_added"])
        return

    if context.user_data.get("state") == "adding_ad_phrase":
        chat_id = context.user_data.get("target_chat_id")
    
        try:
            chat = await context.bot.get_chat(chat_id)
    
            if not await is_admin(chat, user_id):
                await message.reply_text(TEXTS[lang]["access_denied"])
                context.user_data.clear()
                return
    
        except Exception as e:
            print("ADD AD PHRASE TEXT ACCESS ERROR:", e)
            await message.reply_text(TEXTS[lang]["access_denied"])
            context.user_data.clear()
            return
    
        phrase = " ".join(message.text.strip().lower().split())
    
        if phrase:
            add_ad_phrases(chat_id, [phrase])
    
        context.user_data.clear()
    
        await message.reply_text(TEXTS[lang]["ad_phrase_added"])
        return

def build_ads_panel(lang: str, chat_id: int, anti_links: bool):
    status = (
        TEXTS[lang]["links_enabled"]
        if anti_links
        else TEXTS[lang]["links_disabled"]
    )

    toggle_text = (
        TEXTS[lang]["btn_disable_links"]
        if anti_links
        else TEXTS[lang]["btn_enable_links"]
    )

    text = TEXTS[lang]["ads_panel"].format(status=status)

    keyboard = [
        [
            InlineKeyboardButton(
                toggle_text,
                callback_data=f"ads_toggle_links:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_other_links"],
                callback_data=f"ad_links_panel:{chat_id}:0"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_ad_phrases"],
                callback_data=f"ad_phrases_panel:{chat_id}:0"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_ad_exceptions"],
                callback_data=f"ad_exceptions_panel:{chat_id}:0"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["back_button"],
                callback_data=f"group_settings:{chat_id}"
            )
        ],
    ]

    return text, InlineKeyboardMarkup(keyboard)

async def ads_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    chat_id = int(query.data.split(":")[1])

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("ADS PANEL ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    settings = get_group_settings(chat_id)

    text, keyboard = build_ads_panel(
        lang=lang,
        chat_id=chat_id,
        anti_links=settings["anti_links"]
    )

    await query.edit_message_text(
        text,
        reply_markup=keyboard
    )

async def ads_toggle_links_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    chat_id = int(query.data.split(":")[1])

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("ADS TOGGLE ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    settings = get_group_settings(chat_id)
    new_value = not settings["anti_links"]

    set_group_setting(chat_id, "anti_links", new_value)

    text, keyboard = build_ads_panel(
        lang=lang,
        chat_id=chat_id,
        anti_links=new_value
    )

    await query.edit_message_text(
        text,
        reply_markup=keyboard
    )

def build_ad_link_pages(rows):
    pages = []
    current_page = []
    current_length = 0

    for index, (_, link) in enumerate(rows, start=1):
        line = f"{index}. {link}"

        line_length = len(line) + 1

        if current_page and current_length + line_length > 3000:
            pages.append(current_page)
            current_page = []
            current_length = 0

        current_page.append(line)
        current_length += line_length

    if current_page:
        pages.append(current_page)

    return pages

def build_ad_links_keyboard(lang: str, chat_id: int, page: int, total_pages: int):
    keyboard = []

    nav_buttons = []

    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                TEXTS[lang]["btn_prev"],
                callback_data=f"ad_links_page:{chat_id}:{page - 1}"
            )
        )

    if page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton(
                TEXTS[lang]["btn_next"],
                callback_data=f"ad_links_page:{chat_id}:{page + 1}"
            )
        )

    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([
        InlineKeyboardButton(
            TEXTS[lang]["btn_add_ad_link"],
            callback_data=f"ad_links_add:{chat_id}"
        )
    ])
    keyboard.append([
        InlineKeyboardButton(
            TEXTS[lang]["btn_delete_ad_link"],
            callback_data=f"ad_links_delete:{chat_id}"
        )
    ])
    keyboard.append([
        InlineKeyboardButton(
            TEXTS[lang]["back_button"],
            callback_data=f"ads_panel:{chat_id}"
        )
    ])

    return InlineKeyboardMarkup(keyboard)

async def ad_links_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    data = query.data.split(":")
    chat_id = int(data[1])
    page = int(data[2]) if len(data) > 2 else 0

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("AD LINKS ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    rows = get_ad_links(chat_id)

    if not rows:
        await query.edit_message_text(
            TEXTS[lang]["ad_links_empty"],
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        TEXTS[lang]["btn_add_ad_link"],
                        callback_data=f"ad_links_add:{chat_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        TEXTS[lang]["back_button"],
                        callback_data=f"ads_panel:{chat_id}"
                    )
                ]
            ])
        )
        return

    pages = build_ad_link_pages(rows)
    total_pages = len(pages)

    if page >= total_pages:
        page = total_pages - 1

    links_text = "\n".join(pages[page])

    await query.edit_message_text(
        TEXTS[lang]["ad_links_title"].format(
            links=links_text,
            page=page + 1,
            total_pages=total_pages
        ),
        reply_markup=build_ad_links_keyboard(
            lang=lang,
            chat_id=chat_id,
            page=page,
            total_pages=total_pages
        ),
        disable_web_page_preview=True
    )

async def add_ad_link_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    chat_id = int(query.data.split(":")[1])

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("ADD AD LINK ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    context.user_data["state"] = "adding_ad_links"
    context.user_data["target_chat_id"] = chat_id

    await query.message.reply_text(TEXTS[lang]["add_ad_link_prompt"])

async def bad_words_search_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    chat_id = int(query.data.split(":")[1])

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("BAD WORD SEARCH ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    context.user_data["state"] = "searching_bad_word"
    context.user_data["target_chat_id"] = chat_id

    await query.message.reply_text(TEXTS[lang]["bad_word_search_prompt"])

async def delete_bad_word_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    _, chat_id, word_id = query.data.split(":")
    chat_id = int(chat_id)
    word_id = int(word_id)

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("DELETE BAD WORD ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    delete_bad_word(chat_id, word_id)

    await query.answer(TEXTS[lang]["bad_word_deleted"], show_alert=True)

    await query.edit_message_text(TEXTS[lang]["bad_word_deleted"])

def build_ad_phrase_pages(rows):
    pages = []
    current_page = []
    current_length = 0

    for index, (_, phrase) in enumerate(rows, start=1):
        line = f"{index}. {phrase}"
        line_length = len(line) + 1

        if current_page and current_length + line_length > 3000:
            pages.append(current_page)
            current_page = []
            current_length = 0

        current_page.append(line)
        current_length += line_length

    if current_page:
        pages.append(current_page)

    return pages

def build_ad_phrases_keyboard(lang: str, chat_id: int, page: int, total_pages: int):
    keyboard = []
    nav_buttons = []

    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                TEXTS[lang]["btn_prev"],
                callback_data=f"ad_phrases_page:{chat_id}:{page - 1}"
            )
        )

    if page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton(
                TEXTS[lang]["btn_next"],
                callback_data=f"ad_phrases_page:{chat_id}:{page + 1}"
            )
        )

    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([
        InlineKeyboardButton(
            TEXTS[lang]["btn_add_ad_phrase"],
            callback_data=f"ad_phrases_add:{chat_id}"
        )
    ])
    keyboard.append([
        InlineKeyboardButton(
            TEXTS[lang]["btn_delete_ad_phrase"],
            callback_data=f"ad_phrases_delete:{chat_id}"
        )
    ])
    keyboard.append([
        InlineKeyboardButton(
            TEXTS[lang]["back_button"],
            callback_data=f"ads_panel:{chat_id}"
        )
    ])

    return InlineKeyboardMarkup(keyboard)

async def ad_phrases_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    data = query.data.split(":")
    chat_id = int(data[1])
    page = int(data[2]) if len(data) > 2 else 0

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("AD PHRASES ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    rows = get_ad_phrases(chat_id)

    if not rows:
        await query.edit_message_text(
            TEXTS[lang]["ad_phrases_empty"],
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        TEXTS[lang]["btn_add_ad_phrase"],
                        callback_data=f"ad_phrases_add:{chat_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        TEXTS[lang]["back_button"],
                        callback_data=f"ads_panel:{chat_id}"
                    )
                ]
            ])
        )
        return

    pages = build_ad_phrase_pages(rows)
    total_pages = len(pages)

    if page >= total_pages:
        page = total_pages - 1

    phrases_text = "\n".join(pages[page])

    await query.edit_message_text(
        TEXTS[lang]["ad_phrases_title"].format(
            phrases=phrases_text,
            page=page + 1,
            total_pages=total_pages
        ),
        reply_markup=build_ad_phrases_keyboard(
            lang=lang,
            chat_id=chat_id,
            page=page,
            total_pages=total_pages
        )
    )

async def add_ad_phrase_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    chat_id = int(query.data.split(":")[1])

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("ADD AD PHRASE ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    context.user_data["state"] = "adding_ad_phrase"
    context.user_data["target_chat_id"] = chat_id

    await query.message.reply_text(TEXTS[lang]["add_ad_phrase_prompt"])

async def delete_ad_link_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    chat_id = int(query.data.split(":")[1])

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("DELETE AD LINK ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    context.user_data["state"] = "deleting_ad_link"
    context.user_data["target_chat_id"] = chat_id

    await query.message.reply_text(TEXTS[lang]["delete_ad_link_prompt"])


async def delete_ad_phrase_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    chat_id = int(query.data.split(":")[1])

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("DELETE AD PHRASE ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    context.user_data["state"] = "deleting_ad_phrase"
    context.user_data["target_chat_id"] = chat_id

    await query.message.reply_text(TEXTS[lang]["delete_ad_phrase_prompt"])

def build_ad_exception_pages(rows):
    pages = []
    current_page = []
    current_length = 0

    for index, (_, exception) in enumerate(rows, start=1):
        line = f"{index}. {exception}"
        line_length = len(line) + 1

        if current_page and current_length + line_length > 3000:
            pages.append(current_page)
            current_page = []
            current_length = 0

        current_page.append(line)
        current_length += line_length

    if current_page:
        pages.append(current_page)

    return pages


def build_ad_exceptions_keyboard(lang: str, chat_id: int, page: int, total_pages: int):
    keyboard = []
    nav_buttons = []

    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                TEXTS[lang]["btn_prev"],
                callback_data=f"ad_exceptions_page:{chat_id}:{page - 1}"
            )
        )

    if page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton(
                TEXTS[lang]["btn_next"],
                callback_data=f"ad_exceptions_page:{chat_id}:{page + 1}"
            )
        )

    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([
        InlineKeyboardButton(
            TEXTS[lang]["btn_add_ad_exception"],
            callback_data=f"ad_exceptions_add:{chat_id}"
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            TEXTS[lang]["btn_delete_ad_exception"],
            callback_data=f"ad_exceptions_delete:{chat_id}"
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            TEXTS[lang]["back_button"],
            callback_data=f"ads_panel:{chat_id}"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


async def ad_exceptions_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    data = query.data.split(":")
    chat_id = int(data[1])
    page = int(data[2]) if len(data) > 2 else 0

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("AD EXCEPTIONS ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    rows = get_ad_exceptions(chat_id)

    if not rows:
        await query.edit_message_text(
            TEXTS[lang]["ad_exceptions_empty"],
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        TEXTS[lang]["btn_add_ad_exception"],
                        callback_data=f"ad_exceptions_add:{chat_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        TEXTS[lang]["back_button"],
                        callback_data=f"ads_panel:{chat_id}"
                    )
                ]
            ])
        )
        return

    pages = build_ad_exception_pages(rows)
    total_pages = len(pages)

    if page >= total_pages:
        page = total_pages - 1

    exceptions_text = "\n".join(pages[page])

    await query.edit_message_text(
        TEXTS[lang]["ad_exceptions_title"].format(
            exceptions=exceptions_text,
            page=page + 1,
            total_pages=total_pages
        ),
        reply_markup=build_ad_exceptions_keyboard(lang, chat_id, page, total_pages),
        disable_web_page_preview=True
    )


async def add_ad_exception_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)
    chat_id = int(query.data.split(":")[1])

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("ADD AD EXCEPTION ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    context.user_data["state"] = "adding_ad_exception"
    context.user_data["target_chat_id"] = chat_id

    await query.message.reply_text(TEXTS[lang]["add_ad_exception_prompt"])


async def delete_ad_exception_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)
    chat_id = int(query.data.split(":")[1])

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("DELETE AD EXCEPTION ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    context.user_data["state"] = "deleting_ad_exception"
    context.user_data["target_chat_id"] = chat_id

    await query.message.reply_text(TEXTS[lang]["delete_ad_exception_prompt"])

def build_warnings_panel(lang: str, chat_id: int, settings: dict):
    bad_words_status = (
        TEXTS[lang]["warn_enabled"]
        if settings["warn_bad_words"]
        else TEXTS[lang]["warn_disabled"]
    )

    ads_status = (
        TEXTS[lang]["warn_enabled"]
        if settings["warn_ads"]
        else TEXTS[lang]["warn_disabled"]
    )

    text = TEXTS[lang]["warnings_panel"].format(
        bad_words_status=bad_words_status,
        ads_status=ads_status,
    )

    bad_words_btn = (
        TEXTS[lang]["btn_warn_bad_words_off"]
        if settings["warn_bad_words"]
        else TEXTS[lang]["btn_warn_bad_words_on"]
    )

    ads_btn = (
        TEXTS[lang]["btn_warn_ads_off"]
        if settings["warn_ads"]
        else TEXTS[lang]["btn_warn_ads_on"]
    )

    keyboard = [
        [
            InlineKeyboardButton(
                bad_words_btn,
                callback_data=f"warnings_toggle:warn_bad_words:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                ads_btn,
                callback_data=f"warnings_toggle:warn_ads:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_bad_words_warn_limit"].format(
                    limit=settings["bad_words_warn_limit"]
                ),
                callback_data=f"warnings_limit:bad_words:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_ads_warn_limit"].format(
                    limit=settings["ads_warn_limit"]
                ),
                callback_data=f"warnings_limit:ads:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["back_button"],
                callback_data=f"group_settings:{chat_id}"
            )
        ],
    ]

    return text, InlineKeyboardMarkup(keyboard)

async def warnings_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    chat_id = int(query.data.split(":")[1])

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("WARNINGS PANEL ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    settings = get_group_settings(chat_id)

    text, keyboard = build_warnings_panel(lang, chat_id, settings)

    await query.edit_message_text(
        text,
        reply_markup=keyboard
    )


async def warnings_toggle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    _, key, chat_id = query.data.split(":")
    chat_id = int(chat_id)

    if key not in ["warn_bad_words", "warn_ads"]:
        return

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("WARNINGS TOGGLE ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    settings = get_group_settings(chat_id)
    new_value = not settings[key]

    set_group_setting(chat_id, key, new_value)

    settings = get_group_settings(chat_id)

    text, keyboard = build_warnings_panel(lang, chat_id, settings)

    await query.edit_message_text(
        text,
        reply_markup=keyboard
    )

def build_warn_limit_keyboard(lang: str, chat_id: int, limit_type: str):
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data=f"warnings_set_limit:{limit_type}:{chat_id}:1"),
            InlineKeyboardButton("2", callback_data=f"warnings_set_limit:{limit_type}:{chat_id}:2"),
            InlineKeyboardButton("3", callback_data=f"warnings_set_limit:{limit_type}:{chat_id}:3"),
        ],
        [
            InlineKeyboardButton("4", callback_data=f"warnings_set_limit:{limit_type}:{chat_id}:4"),
            InlineKeyboardButton("5", callback_data=f"warnings_set_limit:{limit_type}:{chat_id}:5"),
            InlineKeyboardButton("6", callback_data=f"warnings_set_limit:{limit_type}:{chat_id}:6"),
        ],
        [
            InlineKeyboardButton("7", callback_data=f"warnings_set_limit:{limit_type}:{chat_id}:7"),
            InlineKeyboardButton("8", callback_data=f"warnings_set_limit:{limit_type}:{chat_id}:8"),
            InlineKeyboardButton("9", callback_data=f"warnings_set_limit:{limit_type}:{chat_id}:9"),
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["back_button"],
                callback_data=f"warnings_panel:{chat_id}"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)

async def warnings_limit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    _, limit_type, chat_id = query.data.split(":")
    chat_id = int(chat_id)

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("WARNINGS LIMIT ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    await query.edit_message_text(
        TEXTS[lang]["choose_warn_limit"],
        reply_markup=build_warn_limit_keyboard(lang, chat_id, limit_type)
    )


async def warnings_set_limit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    _, limit_type, chat_id, value = query.data.split(":")
    chat_id = int(chat_id)
    value = int(value)

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("WARNINGS SET LIMIT ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    if limit_type == "bad_words":
        key = "bad_words_warn_limit"
    elif limit_type == "ads":
        key = "ads_warn_limit"
    else:
        return

    set_group_number_setting(chat_id, key, value)

    await query.answer(TEXTS[lang]["warn_limit_saved"], show_alert=True)

    settings = get_group_settings(chat_id)
    text, keyboard = build_warnings_panel(lang, chat_id, settings)

    await query.edit_message_text(
        text,
        reply_markup=keyboard
    )

async def send_warning_message(message, lang: str, reason_key: str, count: int, limit: int):
    user = message.from_user

    await message.chat.send_message(
        TEXTS[lang]["warning_message"].format(
            name=user.first_name,
            reason=TEXTS[lang][reason_key],
            count=count,
            limit=limit
        )
    )

async def handle_warning(
    message,
    lang: str,
    reason: str,
    reason_key: str,
    limit: int,
    punish_enabled: bool,
    show_warning: bool,
):
    user = message.from_user

    count = add_warning(message.chat.id, user.id, reason)

    if count >= limit:
        reset_warnings(message.chat.id, user.id, reason)

        if punish_enabled:
            await punish_user_for_warnings(message, lang, reason_key)

        return

    if show_warning:
        await send_warning_message(
            message=message,
            lang=lang,
            reason_key=reason_key,
            count=count,
            limit=limit
        )

async def punish_user_for_warnings(message, lang: str, reason_key: str):
    user = message.from_user

    until_date = datetime.now(timezone.utc) + timedelta(days=1)

    await message.chat.restrict_member(
        user_id=user.id,
        permissions=ChatPermissions(
            can_send_messages=False
        ),
        until_date=until_date
    )

    await message.chat.send_message(
        TEXTS[lang]["limit_reached"].format(
            name=user.first_name,
            reason=TEXTS[lang][reason_key]
        )
    )

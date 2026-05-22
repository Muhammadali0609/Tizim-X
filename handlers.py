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
    reset_warnings,
    remove_group_admin,
    set_punish_duration,
    get_required_subs,
    add_required_sub,
    delete_required_sub_by_index,
    delete_required_sub_by_id
)
from texts import TEXTS
from filters import has_link, has_bad_word, has_ad_phrase, has_custom_ad_link, has_ad_exception, has_username
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

            if await is_admin(chat, user_id):
                valid_groups.append((chat_id, title))
            else:
                remove_group_admin(chat_id, user_id)

        except Exception as e:
            print("CHECK USER GROUP ACCESS ERROR:", e)
            remove_group_admin(chat_id, user_id)

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

    if settings["anti_usernames"] and has_username(text):
        try:
            await message.delete()
        except Exception as e:
            print("DELETE USERNAME ERROR:", e)
    
        return
    
    ad_violation = False

    if has_link(text):
        ad_violation = True

    custom_links = get_ad_links_for_check(message.chat.id)

    if has_custom_ad_link(text, custom_links):
        ad_violation = True

    ad_phrases = get_ad_phrases_for_check(message.chat.id)

    if has_ad_phrase(text, ad_phrases):
        ad_violation = True

    if ad_violation:
        try:
            if settings["anti_links"]:
                await message.delete()

            await handle_warning(
                message=message,
                lang=lang,
                reason="ads",
                reason_key="reason_ads",
                limit=settings["ads_warn_limit"],
                punish_enabled=settings["punish_ads"],
                show_warning=settings["warn_ads"],
                punish_seconds=settings["ads_punish_seconds"],
            )

        except Exception as e:
            print("AD VIOLATION ERROR:", e)

        return

    bad_words = get_bad_words_for_check(message.chat.id)

    if has_bad_word(text, bad_words):
        try:
            if settings["anti_bad_words"]:
                await message.delete()

            await handle_warning(
                message=message,
                lang=lang,
                reason="bad_words",
                reason_key="reason_bad_word",
                limit=settings["bad_words_warn_limit"],
                punish_enabled=settings["punish_bad_words"],
                show_warning=settings["warn_bad_words"],
                punish_seconds=settings["bad_words_punish_seconds"],
            )

        except Exception as e:
            print("BAD WORD VIOLATION ERROR:", e)

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

    settings = get_group_settings(message.chat.id)
    required_subs = await get_valid_required_subs(context, message.chat.id)
    
    if not settings["force_subscribe"] or not required_subs:
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

            keyboard = []

            for _, target_chat, _ in required_subs:
                try:
                    target = await context.bot.get_chat(target_chat)
            
                    username = target_chat.replace("@", "")
            
                    keyboard.append([
                        InlineKeyboardButton(
                            f"📢 {target.title}",
                            url=f"https://t.me/{username}"
                        )
                    ])
            
                except Exception as e:
                    print("GET REQUIRED SUB TITLE ERROR:", e)
            
            keyboard.append([
                InlineKeyboardButton(
                    "✅ Проверить",
                    callback_data=f"check_sub:{message.chat.id}:{user.id}"
                )
            ])

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

    settings = get_group_settings(chat_id)
    required_subs = await get_valid_required_subs(context, chat_id)

    if not settings["force_subscribe"] or not required_subs:
        await query.answer("Sozlama topilmadi", show_alert=True)
        return

    not_subscribed = []

    for _, target_chat, _ in required_subs:
        try:
            member = await context.bot.get_chat_member(
                chat_id=target_chat,
                user_id=target_user_id
            )

            if member.status not in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER,
            ]:
                not_subscribed.append(target_chat)

        except Exception as e:
            print("CHECK REQUIRED SUB ERROR:", e)
            not_subscribed.append(target_chat)

    if not_subscribed:
        await query.answer(
            "❌ Siz barcha kanallarga obuna bo‘lmadingiz",
            show_alert=True
        )
        return

    try:
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

    except Exception as e:
        print("RESTRICT MEMBER ERROR:", e)
        await query.answer("❌ Xatolik yuz berdi", show_alert=True)

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
            InlineKeyboardButton(TEXTS[lang]["btn_restrictions"], callback_data=f"restrictions_panel:{chat_id}"),
        ],
        [
            InlineKeyboardButton(TEXTS[lang]["btn_settings"], callback_data=f"settings_panel:{chat_id}"),
        ],
        [
            InlineKeyboardButton(TEXTS[lang]["btn_required_subs"], callback_data=f"required_subs_panel:{chat_id}")
        ],
        [
            InlineKeyboardButton(TEXTS[lang]["btn_transfer_settings"], callback_data=f"transfer_panel:{chat_id}"),
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

    if context.user_data.get("state") == "adding_required_sub":
        chat_id = context.user_data.get("target_chat_id")
    
        target_chat = normalize_required_sub(message.text)
    
        if not target_chat:
            await message.reply_text(TEXTS[lang]["required_sub_invalid"])
            return
    
        try:
            target = await context.bot.get_chat(target_chat)
    
            if target.type not in ["channel", "group", "supergroup"]:
                await message.reply_text(TEXTS[lang]["required_sub_invalid"])
                return
    
        except Exception as e:
            print("REQUIRED SUB VALIDATION ERROR:", e)
            await message.reply_text(TEXTS[lang]["required_sub_not_accessible"])
            return
    
        add_required_sub(chat_id, target_chat)
    
        context.user_data.clear()
    
        await reply_success_with_back(
            message,
            lang,
            "required_sub_added",
            f"required_subs_panel:{chat_id}"
        )
        return
    
    if context.user_data.get("state") == "deleting_required_sub":
        chat_id = context.user_data.get("target_chat_id")
    
        text = message.text.strip().split()[0]
    
        if not text.isdigit():
            await message.reply_text(TEXTS[lang]["required_sub_not_found"])
            return
    
        deleted = delete_required_sub_by_index(chat_id, int(text))
    
        if not deleted:
            await message.reply_text(TEXTS[lang]["required_sub_not_found"])
            return
    
        context.user_data.clear()
    
        await reply_success_with_back(
            message,
            lang,
            "required_sub_deleted",
            f"required_subs_panel:{chat_id}"
        )
        return
    
    if context.user_data.get("state") == "setting_punish_duration":
        chat_id = context.user_data.get("target_chat_id")
        duration_type = context.user_data.get("duration_type")
    
        try:
            chat = await context.bot.get_chat(chat_id)
    
            if not await is_admin(chat, user_id):
                await message.reply_text(TEXTS[lang]["access_denied"])
                context.user_data.clear()
                return
    
        except Exception as e:
            print("SET DURATION ACCESS ERROR:", e)
            await message.reply_text(TEXTS[lang]["access_denied"])
            context.user_data.clear()
            return
    
        seconds = parse_duration(message.text)
    
        if not seconds:
            await message.reply_text(TEXTS[lang]["invalid_duration_format"])
            return
    
        if duration_type == "bad_words":
            key = "bad_words_punish_seconds"
        elif duration_type == "ads":
            key = "ads_punish_seconds"
        else:
            context.user_data.clear()
            return
    
        set_punish_duration(chat_id, key, seconds)
    
        context.user_data.clear()
    
        await reply_success_with_back(
            message,
            lang,
            "duration_saved",
            f"restrictions_panel:{chat_id}"
        )
        return
    
    if context.user_data.get("state") == "adding_ad_exception":
        chat_id = context.user_data.get("target_chat_id")
    
        exception = message.text.strip().lower()
    
        if exception:
            add_ad_exceptions(chat_id, [exception])
    
        context.user_data.clear()
    
        await reply_success_with_back(
            message,
            lang,
            "ad_exception_added",
            f"ad_exceptions_panel:{chat_id}:0"
        )
        return
    
    
    if context.user_data.get("state") == "deleting_ad_exception":
        chat_id = context.user_data.get("target_chat_id")
    
        text = message.text.strip().split()[0]
    
        if not text.isdigit():
            await message.reply_text(TEXTS[lang]["ad_exception_not_found"])
            return
    
        deleted = delete_ad_exception_by_index(chat_id, int(text))

        if not deleted:
            await message.reply_text(TEXTS[lang]["ad_exception_not_found"])
            return
        
        context.user_data.clear()
        await reply_success_with_back(
            message,
            lang,
            "ad_exception_deleted",
            f"ad_exceptions_panel:{chat_id}:0"
        )
        return
    
    if context.user_data.get("state") == "deleting_ad_link":
        chat_id = context.user_data.get("target_chat_id")
    
        text = message.text.strip().split()[0]
    
        if not text.isdigit():
            await message.reply_text(TEXTS[lang]["ad_link_not_found"])
            return
    
        deleted = delete_ad_link_by_index(chat_id, int(text))

        if not deleted:
            await message.reply_text(TEXTS[lang]["ad_link_not_found"])
            return
        
        context.user_data.clear()
        await reply_success_with_back(
            message,
            lang,
            "ad_link_deleted",
            f"ad_links_panel:{chat_id}:0"
        )
        return
    
    if context.user_data.get("state") == "deleting_ad_phrase":
        chat_id = context.user_data.get("target_chat_id")
    
        text = message.text.strip().split()[0]
    
        if not text.isdigit():
            await message.reply_text(TEXTS[lang]["ad_phrase_not_found"])
            return
    
        deleted = delete_ad_phrase_by_index(chat_id, int(text))

        if not deleted:
            await message.reply_text(TEXTS[lang]["ad_phrase_not_found"])
            return
        
        context.user_data.clear()
        await reply_success_with_back(
            message,
            lang,
            "ad_phrase_deleted",
            f"ad_phrases_panel:{chat_id}:0"
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

        await reply_success_with_back(
            message,
            lang,
            "ad_links_added",
            f"ad_links_panel:{chat_id}:0"
        )
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
    
        if not result:
            await message.reply_text(TEXTS[lang]["bad_word_not_found"])
            return

        context.user_data.clear()
    
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

        await reply_success_with_back(
            message,
            lang,
            "bad_words_added",
            f"bad_words_panel:{chat_id}:0"
        )
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
    
        await reply_success_with_back(
            message,
            lang,
            "ad_phrase_added",
            f"ad_phrases_panel:{chat_id}:0"
        )
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

    await query.edit_message_text(
        TEXTS[lang]["bad_word_deleted"],
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    TEXTS[lang]["btn_open_section"],
                    callback_data=f"bad_words_panel:{chat_id}:0"
                )
            ]
        ])
    )

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
    punish_seconds: int,
):
    user = message.from_user

    count = add_warning(message.chat.id, user.id, reason)

    if count >= limit:
        reset_warnings(message.chat.id, user.id, reason)

        if punish_enabled:
            await punish_user_for_warnings(
                message,
                lang,
                reason_key,
                punish_seconds
            )

        return

    if show_warning:
        await send_warning_message(
            message=message,
            lang=lang,
            reason_key=reason_key,
            count=count,
            limit=limit
        )

async def punish_user_for_warnings(message, lang: str, reason_key: str, seconds: int):
    user = message.from_user

    if seconds == -1:
        until_date = None
    else:
        until_date = datetime.now(timezone.utc) + timedelta(seconds=seconds)

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
            duration=format_duration(seconds, lang),
            reason=TEXTS[lang][reason_key]
        )
    )

def format_duration(seconds: int, lang: str) -> str:
    if seconds == -1:
        return "Навсегда" if lang == "ru" else "Doimiy"
    
    units = [
        (2592000, "месяц", "месяца", "месяцев", "oy"),
        (604800, "неделя", "недели", "недель", "hafta"),
        (86400, "день", "дня", "дней", "kun"),
        (3600, "час", "часа", "часов", "soat"),
        (60, "минута", "минуты", "минут", "daqiqa"),
        (1, "секунда", "секунды", "секунд", "soniya"),
    ]

    parts = []

    for unit_seconds, ru_one, ru_two, ru_many, uz_word in units:
        value = seconds // unit_seconds

        if value:
            seconds %= unit_seconds

            if lang == "ru":
                if value % 10 == 1 and value % 100 != 11:
                    word = ru_one
                elif value % 10 in [2, 3, 4] and value % 100 not in [12, 13, 14]:
                    word = ru_two
                else:
                    word = ru_many

                parts.append(f"{value} {word}")
            else:
                parts.append(f"{value} {uz_word}")

    return " ".join(parts) if parts else ("0 секунд" if lang == "ru" else "0 soniya")

def build_restrictions_panel(lang: str, chat_id: int, settings: dict):
    bad_words_status = (
        TEXTS[lang]["warn_enabled"]
        if settings["punish_bad_words"]
        else TEXTS[lang]["warn_disabled"]
    )

    ads_status = (
        TEXTS[lang]["warn_enabled"]
        if settings["punish_ads"]
        else TEXTS[lang]["warn_disabled"]
    )

    text = TEXTS[lang]["restrictions_panel"].format(
        bad_words_status=bad_words_status,
        ads_status=ads_status,
        bad_words_duration=format_duration(settings["bad_words_punish_seconds"], lang),
        ads_duration=format_duration(settings["ads_punish_seconds"], lang),
    )

    bad_words_btn = (
        TEXTS[lang]["btn_punish_bad_words_off"]
        if settings["punish_bad_words"]
        else TEXTS[lang]["btn_punish_bad_words_on"]
    )

    ads_btn = (
        TEXTS[lang]["btn_punish_ads_off"]
        if settings["punish_ads"]
        else TEXTS[lang]["btn_punish_ads_on"]
    )

    keyboard = [
        [
            InlineKeyboardButton(
                bad_words_btn,
                callback_data=f"restrictions_toggle:punish_bad_words:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                ads_btn,
                callback_data=f"restrictions_toggle:punish_ads:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_bad_words_punish_duration"],
                callback_data=f"restrictions_duration:bad_words:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_ads_punish_duration"],
                callback_data=f"restrictions_duration:ads:{chat_id}"
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

async def restrictions_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        print("RESTRICTIONS PANEL ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    settings = get_group_settings(chat_id)
    text, keyboard = build_restrictions_panel(lang, chat_id, settings)

    await query.edit_message_text(text, reply_markup=keyboard)


async def restrictions_toggle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    _, key, chat_id = query.data.split(":")
    chat_id = int(chat_id)

    if key not in ["punish_bad_words", "punish_ads"]:
        return

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("RESTRICTIONS TOGGLE ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    settings = get_group_settings(chat_id)
    new_value = not settings[key]

    set_group_setting(chat_id, key, new_value)

    settings = get_group_settings(chat_id)
    text, keyboard = build_restrictions_panel(lang, chat_id, settings)

    await query.edit_message_text(text, reply_markup=keyboard)

def parse_duration(text: str):
    text = text.lower().strip()

    if text in ["forever", "навсегда"]:
        return -1
        
    units = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400,
        "w": 604800,
        "mo": 2592000,
    }

    max_seconds = 365 * 24 * 60 * 60
    parts = text.lower().split()

    if not parts:
        return None

    used_units = set()
    total_seconds = 0

    for part in parts:
        match = re.fullmatch(r"(\d+)(mo|s|m|h|d|w)", part)

        if not match:
            return None

        value = int(match.group(1))
        unit = match.group(2)

        if value <= 0:
            return None

        if unit in used_units:
            return None

        used_units.add(unit)
        total_seconds += value * units[unit]

        if total_seconds > max_seconds:
            return None

    return total_seconds

async def restrictions_duration_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    _, duration_type, chat_id = query.data.split(":")
    chat_id = int(chat_id)

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("RESTRICTIONS DURATION ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    context.user_data["state"] = "setting_punish_duration"
    context.user_data["target_chat_id"] = chat_id
    context.user_data["duration_type"] = duration_type

    await query.message.reply_text(TEXTS[lang]["enter_duration_prompt"])

async def reply_success_with_back(message, lang: str, text_key: str, callback_data: str):
    await message.reply_text(
        TEXTS[lang][text_key],
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    TEXTS[lang]["btn_open_section"],
                    callback_data=callback_data
                )
            ]
        ])
    )

def build_settings_panel(lang: str, chat_id: int, settings: dict):
    bad_words_status = (
        TEXTS[lang]["warn_enabled"]
        if settings["anti_bad_words"]
        else TEXTS[lang]["warn_disabled"]
    )

    ads_status = (
        TEXTS[lang]["warn_enabled"]
        if settings["anti_links"]
        else TEXTS[lang]["warn_disabled"]
    )

    usernames_status = (
        TEXTS[lang]["warn_enabled"]
        if settings["anti_usernames"]
        else TEXTS[lang]["warn_disabled"]
    )

    text = TEXTS[lang]["settings_panel"].format(
        bad_words_status=bad_words_status,
        ads_status=ads_status,
        usernames_status=usernames_status,
    )

    bad_words_btn = (
        TEXTS[lang]["btn_toggle_bad_words_off"]
        if settings["anti_bad_words"]
        else TEXTS[lang]["btn_toggle_bad_words_on"]
    )

    ads_btn = (
        TEXTS[lang]["btn_toggle_ads_off"]
        if settings["anti_links"]
        else TEXTS[lang]["btn_toggle_ads_on"]
    )

    usernames_btn = (
        TEXTS[lang]["btn_toggle_usernames_off"]
        if settings["anti_usernames"]
        else TEXTS[lang]["btn_toggle_usernames_on"]
    )

    keyboard = [
        [
            InlineKeyboardButton(
                bad_words_btn,
                callback_data=f"settings_toggle:anti_bad_words:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                ads_btn,
                callback_data=f"settings_toggle:anti_links:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                usernames_btn,
                callback_data=f"settings_toggle:anti_usernames:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["back_button"],
                callback_data=f"group_settings:{chat_id}"
            )
        ]
    ]

    return text, InlineKeyboardMarkup(keyboard)

async def settings_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        print("SETTINGS PANEL ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    settings = get_group_settings(chat_id)

    text, keyboard = build_settings_panel(lang, chat_id, settings)

    await query.edit_message_text(
        text,
        reply_markup=keyboard
    )


async def settings_toggle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    _, key, chat_id = query.data.split(":")
    chat_id = int(chat_id)

    allowed = [
        "anti_bad_words",
        "anti_links",
        "anti_usernames",
    ]

    if key not in allowed:
        return

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("SETTINGS TOGGLE ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    settings = get_group_settings(chat_id)

    set_group_setting(chat_id, key, not settings[key])

    settings = get_group_settings(chat_id)

    text, keyboard = build_settings_panel(lang, chat_id, settings)

    await query.edit_message_text(
        text,
        reply_markup=keyboard
    )

def build_required_subs_panel(lang: str, chat_id: int, settings: dict, rows):
    status = (
        TEXTS[lang]["warn_enabled"]
        if settings["force_subscribe"]
        else TEXTS[lang]["warn_disabled"]
    )

    toggle_text = (
        TEXTS[lang]["btn_required_subs_off"]
        if settings["force_subscribe"]
        else TEXTS[lang]["btn_required_subs_on"]
    )

    if rows:
        subs_text = "\n".join(
            f"{i}. {target_chat}"
            for i, (_, target_chat, _) in enumerate(rows, start=1)
        )
    else:
        subs_text = TEXTS[lang]["required_subs_empty"]

    text = TEXTS[lang]["required_subs_panel"].format(
        status=status,
        subs=subs_text
    )

    keyboard = [
        [
            InlineKeyboardButton(
                toggle_text,
                callback_data=f"required_subs_toggle:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_add_required_sub"],
                callback_data=f"required_subs_add:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_delete_required_sub"],
                callback_data=f"required_subs_delete:{chat_id}"
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

async def required_subs_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        print("REQUIRED SUBS PANEL ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    valid_rows = await get_valid_required_subs(context, chat_id)
    settings = get_group_settings(chat_id)
    
    text, keyboard = build_required_subs_panel(lang, chat_id, settings, valid_rows)

    await query.edit_message_text(
        text,
        reply_markup=keyboard
    )


async def required_subs_toggle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        print("REQUIRED SUBS TOGGLE ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    valid_rows = await get_valid_required_subs(context, chat_id)
    settings = get_group_settings(chat_id)

    new_value = not settings["force_subscribe"]

    if new_value and not valid_rows:
        await query.answer(
            TEXTS[lang]["required_subs_empty_alert"],
            show_alert=True
        )
        return

    set_group_setting(chat_id, "force_subscribe", new_value)

    valid_rows = await get_valid_required_subs(context, chat_id)
    settings = get_group_settings(chat_id)

    text, keyboard = build_required_subs_panel(
        lang,
        chat_id,
        settings,
        valid_rows
    )

    await query.edit_message_text(
        text,
        reply_markup=keyboard
    )

async def add_required_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        print("ADD REQUIRED SUB ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    context.user_data["state"] = "adding_required_sub"
    context.user_data["target_chat_id"] = chat_id

    await query.message.reply_text(TEXTS[lang]["add_required_sub_prompt"])


async def delete_required_sub_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        print("DELETE REQUIRED SUB ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    context.user_data["state"] = "deleting_required_sub"
    context.user_data["target_chat_id"] = chat_id

    await query.message.reply_text(TEXTS[lang]["delete_required_sub_prompt"])

def normalize_required_sub(text: str):
    text = text.strip()

    if text.startswith("@"):
        username = text[1:]
    else:
        match = re.fullmatch(r"https://t\.me/([a-zA-Z0-9_]{5,32})/?", text)
        if not match:
            return None

        username = match.group(1)

    if not re.fullmatch(r"[a-zA-Z0-9_]{5,32}", username):
        return None

    return f"@{username}"

async def get_valid_required_subs(context, chat_id: int):
    rows = get_required_subs(chat_id)
    valid_rows = []

    for sub_id, target_chat, invite_link in rows:
        try:
            await context.bot.get_chat(target_chat)
            valid_rows.append((sub_id, target_chat, invite_link))

        except Exception as e:
            print("REMOVE BROKEN REQUIRED SUB:", target_chat, e)
            delete_required_sub_by_id(sub_id)

    if not valid_rows:
        set_group_setting(chat_id, "force_subscribe", False)

    return valid_rows

def get_transfer_state(context, chat_id: int):
    key = f"transfer:{chat_id}"

    if key not in context.user_data:
        context.user_data[key] = {
            "bad_words": True,
            "ads": True,
            "warnings": True,
            "restrictions": True,
            "delete_settings": True,
        }

    return context.user_data[key]

def build_transfer_panel(lang: str, chat_id: int, state: dict):
    def status(value: bool):
        return "✅" if value else "❌"

    keyboard = [
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_transfer_bad_words"].format(
                    status=status(state["bad_words"])
                ),
                callback_data=f"transfer_toggle:bad_words:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_transfer_ads"].format(
                    status=status(state["ads"])
                ),
                callback_data=f"transfer_toggle:ads:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_transfer_warnings"].format(
                    status=status(state["warnings"])
                ),
                callback_data=f"transfer_toggle:warnings:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_transfer_restrictions"].format(
                    status=status(state["restrictions"])
                ),
                callback_data=f"transfer_toggle:restrictions:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_transfer_delete_settings"].format(
                    status=status(state["delete_settings"])
                ),
                callback_data=f"transfer_toggle:delete_settings:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_transfer_all"],
                callback_data=f"transfer_all:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_transfer_selected"],
                callback_data=f"transfer_selected:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["back_button"],
                callback_data=f"group_settings:{chat_id}"
            )
        ],
    ]

    return TEXTS[lang]["transfer_panel"], InlineKeyboardMarkup(keyboard)

async def transfer_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        print("TRANSFER PANEL ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    state = get_transfer_state(context, chat_id)

    text, keyboard = build_transfer_panel(lang, chat_id, state)

    await query.edit_message_text(
        text,
        reply_markup=keyboard
    )


async def transfer_toggle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    _, key, chat_id = query.data.split(":")
    chat_id = int(chat_id)

    allowed = [
        "bad_words",
        "ads",
        "warnings",
        "restrictions",
        "delete_settings",
    ]

    if key not in allowed:
        return

    state = get_transfer_state(context, chat_id)
    state[key] = not state[key]

    text, keyboard = build_transfer_panel(lang, chat_id, state)

    await query.edit_message_text(
        text,
        reply_markup=keyboard
    )


async def transfer_all_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    source_chat_id = int(query.data.split(":")[1])

    state = get_transfer_state(context, source_chat_id)

    for key in state:
        state[key] = True

    target_groups = await get_valid_target_groups(context, user_id, source_chat_id)

    if not target_groups:
        await query.answer(
            TEXTS[lang]["transfer_no_target_groups"],
            show_alert=True
        )
        return

    keyboard = []

    for chat_id, title in target_groups:
        keyboard.append([
            InlineKeyboardButton(
                title,
                callback_data=f"transfer_target:{source_chat_id}:{chat_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            TEXTS[lang]["back_button"],
            callback_data=f"transfer_panel:{source_chat_id}"
        )
    ])

    await query.edit_message_text(
        TEXTS[lang]["transfer_choose_group"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def transfer_selected_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    source_chat_id = int(query.data.split(":")[1])

    state = get_transfer_state(context, source_chat_id)

    if not any(state.values()):
        await query.answer(
            TEXTS[lang]["transfer_nothing_selected"],
            show_alert=True
        )
        return

    target_groups = await get_valid_target_groups(context, user_id, source_chat_id)

    if not target_groups:
        await query.answer(
            TEXTS[lang]["transfer_no_target_groups"],
            show_alert=True
        )
        return

    keyboard = []

    for chat_id, title in target_groups:
        keyboard.append([
            InlineKeyboardButton(
                title,
                callback_data=f"transfer_target:{source_chat_id}:{chat_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            TEXTS[lang]["back_button"],
            callback_data=f"transfer_panel:{source_chat_id}"
        )
    ])

    await query.edit_message_text(
        TEXTS[lang]["transfer_choose_group"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def get_valid_target_groups(context, user_id: int, source_chat_id: int):
    groups = get_user_groups(user_id)
    valid_groups = []

    for chat_id, title in groups:
        if chat_id == source_chat_id:
            continue

        try:
            chat = await context.bot.get_chat(chat_id)

            if await is_admin(chat, user_id):
                valid_groups.append((chat_id, title))

        except Exception as e:
            print("TRANSFER TARGET GROUP ERROR:", e)

    return valid_groups

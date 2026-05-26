from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions, ReplyKeyboardMarkup, ChatMemberOwner
from telegram.constants import ChatMemberStatus
from telegram.ext import ContextTypes
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
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
    delete_required_sub_by_id,
    copy_settings,
    get_group_plan,
    save_group_owner,
    is_group_active,
    get_required_contacts_limit,
    set_required_contacts_limit,
    get_required_contacts_total_invites,
    reset_required_contacts_invites,
    add_required_contact_invites,
    get_required_contacts_limit,
    get_user_required_contacts_count,
)
from texts import TEXTS
from filters import has_link, has_bad_word, has_ad_phrase, has_custom_ad_link, has_ad_exception, has_username
from admins import is_admin
import asyncio
import math
import re

import time

PRIVATE_MESSAGE_LIMIT = {}
CALLBACK_LIMIT = {}


def is_private_message_limited(user_id: int) -> bool:
    now = time.time()

    last_time = PRIVATE_MESSAGE_LIMIT.get(user_id, 0)

    if now - last_time < 1:
        return True

    PRIVATE_MESSAGE_LIMIT[user_id] = now
    return False


def is_callback_limited(user_id: int) -> bool:
    now = time.time()

    data = CALLBACK_LIMIT.get(user_id, [])

    data = [
        timestamp for timestamp in data
        if now - timestamp <= 60
    ]

    if len(data) >= 30:
        CALLBACK_LIMIT[user_id] = data
        return True

    data.append(now)
    CALLBACK_LIMIT[user_id] = data

    return False

async def check_callback_limit(query) -> bool:
    user_id = query.from_user.id

    if is_callback_limited(user_id):
        await query.answer()
        return True

    return False

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if is_private_message_limited(user_id):
        return
    
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

    save_user_language(user_id, lang, query.from_user.first_name)

    keyboard_text = (
        TEXTS[lang]["manage_button"]
    )
    
    language_text = (
        TEXTS[lang]["language_button"]
    )

    keyboard = ReplyKeyboardMarkup(
        [
            [keyboard_text, language_text],
            [TEXTS[lang]["guide_button"]],
        ],
        resize_keyboard=True
    )

    await query.answer(TEXTS[lang]["language_saved"])

    await query.message.reply_text(
        TEXTS[lang]["start"],
        reply_markup=keyboard,
        parse_mode="HTML"
    )

    try:
        await query.message.delete()
    except Exception as e:
        print("DELETE LANGUAGE MESSAGE ERROR:", e)

async def language_toggle_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or message.chat.type != "private":
        return

    user_id = message.from_user.id

    if is_private_message_limited(user_id):
        return

    current_lang = get_user_language(user_id)

    new_lang = "uz" if current_lang == "ru" else "ru"

    save_user_language(user_id, new_lang)

    keyboard = ReplyKeyboardMarkup(
        [
            [
                TEXTS[new_lang]["manage_button"],
                TEXTS[new_lang]["language_button"],
            ],
            [
                TEXTS[new_lang]["guide_button"],
            ],
        ],
        resize_keyboard=True
    )

    await message.reply_text(
        TEXTS[new_lang]["language_saved"],
        reply_markup=keyboard
    )

async def settings_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = update.effective_user.id
    
    if is_private_message_limited(user_id):
        return

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
    save_group(chat.id, chat.title, chat.type, chat.username)
    await sync_group_admins(chat, context)
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

    if not is_group_active(message.chat.id):
        return

    limit = get_required_contacts_limit(message.chat.id)

    if limit > 0:
        user = message.from_user
    
        if user and not user.is_bot:
            if not await is_admin(message.chat, user.id):
                added = get_user_required_contacts_count(message.chat.id, user.id)
    
                if added < limit:
                    try:
                        await message.delete()
                    except Exception as e:
                        print("DELETE REQUIRED CONTACT MESSAGE ERROR:", e)
    
                    lang = get_group_language(message.chat.id)
    
                    until_date = datetime.now(timezone.utc) + timedelta(minutes=5)

                    try:
                        await message.chat.restrict_member(
                            user_id=user.id,
                            permissions=ChatPermissions(
                                can_send_messages=False
                            ),
                            until_date=until_date
                        )
                    except Exception as e:
                        print("REQUIRED CONTACTS MUTE ERROR:", e)
                    
                    notice = await message.chat.send_message(
                        TEXTS[lang]["required_contacts_need_invite"].format(
                            need=limit
                        ),
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton(
                                    TEXTS[lang]["required_contacts_check"],
                                    callback_data=f"check_required_contacts:{message.chat.id}:{user.id}"
                                )
                            ]
                        ])
                    )
                    
                    async def delete_required_contacts_notice():
                        await asyncio.sleep(300)
                    
                        try:
                            await notice.delete()
                        except Exception as e:
                            print("DELETE REQUIRED CONTACTS NOTICE ERROR:", e)
                    
                    context.application.create_task(delete_required_contacts_notice())
                    
                    return

    save_group(message.chat.id, message.chat.title, message.chat.type, message.chat.username)

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

    if not is_group_active(message.chat.id):
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

    save_group(message.chat.id, message.chat.title, message.chat.type, message.chat.username)
    await sync_group_admins(message.chat, context)
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

    if not is_group_active(message.chat.id):
        return

    inviter = message.from_user

    if inviter and not inviter.is_bot:
        invited_user_ids = [
            user.id
            for user in message.new_chat_members
            if not user.is_bot
        ]
    
        add_required_contact_invites(
            message.chat.id,
            inviter.id,
            invited_user_ids
        )

    settings = get_group_settings(message.chat.id)
    lang = get_group_language(message.chat.id)
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
                    TEXTS[lang]["required_sub_check_button"],
                    callback_data=f"check_sub:{message.chat.id}:{user.id}"
                )
            ])

            await message.chat.send_message(
                TEXTS[lang]["required_sub_join_text"].format(
                    name=f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
                ),
                parse_mode="HTML",
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

    if not is_group_active(query.message.chat.id):
        return

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
            
    lang = get_group_language(chat_id)
    if not_subscribed:
        await query.answer(
            TEXTS[lang]["required_sub_not_all"],
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

        await query.answer(TEXTS[lang]["required_sub_success"], show_alert=True)

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

    if await check_callback_limit(query):
        return
        
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
            InlineKeyboardButton(TEXTS[lang]["btn_required_contacts"], callback_data=f"required_contacts_panel:{chat_id}")
        ],
        [
            InlineKeyboardButton(TEXTS[lang]["btn_transfer_settings"], callback_data=f"transfer_panel:{chat_id}"),
        ],
        [
            InlineKeyboardButton(TEXTS[lang]["btn_group_plan"], callback_data=f"group_plan:{chat_id}")
        ],
        [
            InlineKeyboardButton(TEXTS[lang]["back_button"], callback_data="back_groups")
        ],
    ]

    await query.edit_message_text(
        TEXTS[lang]["group_panel"].format(
            title=chat.title,
            chat_id=chat_id
        ),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def back_groups_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if is_private_message_limited(user_id):
        return

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
    
            bot_member = await context.bot.get_chat_member(
                chat_id=target_chat,
                user_id=context.bot.id
            )
    
            if bot_member.status not in [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER,
            ]:
                await message.reply_text(TEXTS[lang]["required_sub_not_accessible"])
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

    if context.user_data.get("state") == "setting_required_contacts_limit":
        chat_id = context.user_data.get("target_chat_id")
        lang = get_group_language(chat_id)
    
        text = message.text.strip()
    
        if not text.isdigit():
            await message.reply_text(TEXTS[lang]["required_contacts_invalid_limit"])
            return
    
        limit = int(text)
    
        if limit < 0 or limit > 200:
            await message.reply_text(TEXTS[lang]["required_contacts_invalid_limit"])
            return
    
        set_required_contacts_limit(chat_id, limit)
    
        context.user_data.clear()
    
        await reply_success_with_back(
            message,
            lang,
            "required_contacts_limit_saved",
            f"required_contacts_panel:{chat_id}"
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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
    target_user=None,
):
    user = target_user or message.from_user

    count = add_warning(message.chat.id, user.id, reason)

    if count >= limit:
        reset_warnings(message.chat.id, user.id, reason)

        if punish_enabled:
            await punish_user_for_warnings(
                message,
                lang,
                reason_key,
                punish_seconds,
                show_message=show_warning,
                target_user=user
            )

        return

    if show_warning:
        await message.chat.send_message(
            TEXTS[lang]["warning_message"].format(
                name=user.first_name,
                reason=TEXTS[lang][reason_key],
                count=count,
                limit=limit
            )
        )

async def punish_user_for_warnings(
    message,
    lang: str,
    reason_key: str,
    seconds: int,
    show_message: bool = True,
    target_user=None,
):
    user = target_user or message.from_user

    if seconds == -2:
        await message.chat.ban_member(
            user_id=user.id
        )

        if show_message:
            await message.chat.send_message(
                TEXTS[lang]["limit_reached_ban"].format(
                    name=user.first_name,
                    reason=TEXTS[lang][reason_key]
                )
            )

        return
    
    if seconds == -1:
        until_date = None
    else:
        until_date = datetime.now(timezone.utc) + timedelta(seconds=seconds)

    await message.chat.restrict_member(
        user_id=user.id,
        permissions=ChatPermissions(can_send_messages=False),
        until_date=until_date
    )

    if show_message:
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

    if seconds == -2:
        return "Бан" if lang == "ru" else "Ban"

    units = [
        ("mo", 2592000),
        ("w", 604800),
        ("d", 86400),
        ("h", 3600),
        ("m", 60),
        ("s", 1),
    ]

    names = {
        "ru": {
            "mo": ("месяц", "месяца", "месяцев"),
            "w": ("неделя", "недели", "недель"),
            "d": ("день", "дня", "дней"),
            "h": ("час", "часа", "часов"),
            "m": ("минута", "минуты", "минут"),
            "s": ("секунда", "секунды", "секунд"),
        },
        "uz": {
            "mo": "oy",
            "w": "hafta",
            "d": "kun",
            "h": "soat",
            "m": "daqiqa",
            "s": "soniya",
        }
    }

    parts = []

    for unit, unit_seconds in units:
        value = seconds // unit_seconds

        if value <= 0:
            continue

        seconds %= unit_seconds

        if lang == "ru":
            if value % 10 == 1 and value % 100 != 11:
                word = names["ru"][unit][0]
            elif value % 10 in [2, 3, 4] and value % 100 not in [12, 13, 14]:
                word = names["ru"][unit][1]
            else:
                word = names["ru"][unit][2]

            parts.append(f"{value} {word}")

        else:
            parts.append(f"{value} {names['uz'][unit]}")

    return " ".join(parts)

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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if text in ["ban", "бан"]:
        return -2
        
    units = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400,
        "w": 604800,
        "mo": 2592000,
    }

    min_seconds = 60
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

    if total_seconds != -1 and total_seconds < min_seconds:
        return None

    return total_seconds

async def restrictions_duration_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

    if await check_callback_limit(query):
        return
    
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

def build_transfer_items_text(lang: str, state: dict):
    items = []

    if state["bad_words"]:
        items.append(TEXTS[lang]["transfer_item_bad_words"])

    if state["ads"]:
        items.append(TEXTS[lang]["transfer_item_ads"])

    if state["warnings"]:
        items.append(TEXTS[lang]["transfer_item_warnings"])

    if state["restrictions"]:
        items.append(TEXTS[lang]["transfer_item_restrictions"])

    if state["delete_settings"]:
        items.append(TEXTS[lang]["transfer_item_delete_settings"])

    return "\n".join(items)

async def transfer_target_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if await check_callback_limit(query):
        return
    
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    _, source_chat_id, target_chat_id = query.data.split(":")
    source_chat_id = int(source_chat_id)
    target_chat_id = int(target_chat_id)

    try:
        source_chat = await context.bot.get_chat(source_chat_id)
        target_chat = await context.bot.get_chat(target_chat_id)

        if not await is_admin(source_chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

        if not await is_admin(target_chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("TRANSFER TARGET ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    state = get_transfer_state(context, source_chat_id)

    items_text = build_transfer_items_text(lang, state)

    keyboard = [
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_confirm"],
                callback_data=f"transfer_confirm:{source_chat_id}:{target_chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["back_button"],
                callback_data=f"transfer_selected:{source_chat_id}"
            )
        ],
    ]

    await query.edit_message_text(
        TEXTS[lang]["transfer_confirm_text"].format(
            source_title=source_chat.title,
            target_title=target_chat.title,
            items=items_text
        ),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def transfer_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if await check_callback_limit(query):
        return
    
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    _, source_chat_id, target_chat_id = query.data.split(":")
    source_chat_id = int(source_chat_id)
    target_chat_id = int(target_chat_id)

    try:
        source_chat = await context.bot.get_chat(source_chat_id)
        target_chat = await context.bot.get_chat(target_chat_id)

        if not await is_admin(source_chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

        if not await is_admin(target_chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("TRANSFER CONFIRM ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    state = get_transfer_state(context, source_chat_id)

    if not any(state.values()):
        await query.answer(
            TEXTS[lang]["transfer_nothing_selected"],
            show_alert=True
        )
        return

    copy_settings(source_chat_id, target_chat_id, state)

    context.user_data.pop(f"transfer:{source_chat_id}", None)

    await query.edit_message_text(
        TEXTS[lang]["transfer_done"]
    )

async def group_plan_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if await check_callback_limit(query):
        return
    
    user_id = query.from_user.id
    lang = get_user_language(user_id)

    chat_id = int(query.data.split(":")[1])

    try:
        chat = await context.bot.get_chat(chat_id)

        if not await is_admin(chat, user_id):
            await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
            return

    except Exception as e:
        print("GROUP PLAN ACCESS ERROR:", e)
        await query.answer(TEXTS[lang]["access_denied"], show_alert=True)
        return

    plan_name, expires_at = get_group_plan(chat_id)

    plan_text = TEXTS[lang].get(f"plan_{plan_name}", plan_name)

    if expires_at:
        local_time = expires_at.astimezone(
            ZoneInfo("Asia/Tashkent")
        )
        expires_text = local_time.strftime("%d.%m.%Y %H:%M")
    else:
        expires_text = "—"

    keyboard = [
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_pay_plan"],
                callback_data=f"pay_plan:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["back_button"],
                callback_data=f"group_settings:{chat_id}"
            )
        ],
    ]

    await query.edit_message_text(
        TEXTS[lang]["group_plan_text"].format(
            plan=plan_text,
            expires_at=expires_text
        ),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def delete_admin_command(message):
    try:
        await message.delete()
    except Exception as e:
        print("DELETE ADMIN COMMAND ERROR:", e)

async def resolve_mute_target(message, context, args):
    if message.reply_to_message:
        return message.reply_to_message.from_user

    if not args:
        return None

    raw_target = args[0].strip()

    if raw_target.isdigit():
        try:
            member = await context.bot.get_chat_member(
                chat_id=message.chat.id,
                user_id=int(raw_target)
            )
            return member.user
        except Exception as e:
            print("MUTE ID FIND ERROR:", e)
            return None

    if raw_target.startswith("@"):
        try:
            member = await context.bot.get_chat_member(
                chat_id=message.chat.id,
                user_id=raw_target
            )
            return member.user
        except Exception as e:
            print("MUTE USERNAME FIND ERROR:", e)
            return None

    return None

async def apply_manual_mute(message, context, target_user, seconds, lang):
    if seconds == -1:
        until_date = None
    else:
        until_date = datetime.now(timezone.utc) + timedelta(seconds=seconds)

    await message.chat.restrict_member(
        user_id=target_user.id,
        permissions=ChatPermissions(
            can_send_messages=False
        ),
        until_date=until_date
    )

    msg = await message.chat.send_message(
        TEXTS[lang]["user_muted"].format(
            name=target_user.first_name,
            duration=format_duration(seconds, lang)
        )
    )

async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or message.chat.type not in ["group", "supergroup"]:
        return

    await delete_admin_command(message)

    user = message.from_user
    lang = get_group_language(message.chat.id)

    if not await is_admin(message.chat, user.id):
        return

    args = context.args

    target_user = await resolve_mute_target(message, context, args)

    if not target_user:
        msg = await message.chat.send_message(TEXTS[lang]["user_not_found"])
        await asyncio.sleep(3)
        await msg.delete()
        return

    if message.reply_to_message:
        duration_text = args[0] if args else "forever"
    else:
        duration_text = args[1] if len(args) >= 2 else "forever"

    seconds = parse_duration(duration_text)

    if seconds is None:
        msg = await message.chat.send_message(TEXTS[lang]["invalid_mute_duration"])
        await asyncio.sleep(3)
        await msg.delete()
        return

    try:
        await apply_manual_mute(message, context, target_user, seconds, lang)
    except Exception as e:
        print("MANUAL MUTE ERROR:", e)

async def dmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or message.chat.type not in ["group", "supergroup"]:
        return

    await delete_admin_command(message)

    user = message.from_user
    lang = get_group_language(message.chat.id)

    if not await is_admin(message.chat, user.id):
        return

    if not message.reply_to_message:
        msg = await message.chat.send_message(TEXTS[lang]["user_not_found"])
        await asyncio.sleep(3)
        await msg.delete()
        return

    target_user = message.reply_to_message.from_user
    duration_text = context.args[0] if context.args else "forever"

    seconds = parse_duration(duration_text)

    if seconds is None:
        msg = await message.chat.send_message(TEXTS[lang]["invalid_mute_duration"])
        await asyncio.sleep(3)
        await msg.delete()
        return

    try:
        await message.reply_to_message.delete()
    except Exception as e:
        print("DELETE DMUTE TARGET MESSAGE ERROR:", e)

    try:
        await apply_manual_mute(message, context, target_user, seconds, lang)
    except Exception as e:
        print("DMUTE ERROR:", e)

async def manual_warn(update: Update, context: ContextTypes.DEFAULT_TYPE, reason: str):
    message = update.message

    if not message or message.chat.type not in ["group", "supergroup"]:
        return

    await delete_admin_command(message)

    admin = message.from_user
    lang = get_group_language(message.chat.id)

    if not await is_admin(message.chat, admin.id):
        return

    target_user = await resolve_mute_target(message, context, context.args)

    if not target_user:
        msg = await message.chat.send_message(TEXTS[lang]["user_not_found"])
        await asyncio.sleep(3)
        await msg.delete()
        return

    settings = get_group_settings(message.chat.id)

    if reason == "bad_words":

        await handle_warning(
            message=message,
            lang=lang,
            reason="bad_words",
            reason_key="reason_bad_word",
            limit=settings["bad_words_warn_limit"],
            punish_enabled=settings["punish_bad_words"],
            show_warning=True,
            punish_seconds=settings["bad_words_punish_seconds"],
            target_user=target_user,
        )

    elif reason == "ads":

        await handle_warning(
            message=message,
            lang=lang,
            reason="ads",
            reason_key="reason_ads",
            limit=settings["ads_warn_limit"],
            punish_enabled=settings["punish_ads"],
            show_warning=True,
            punish_seconds=settings["ads_punish_seconds"],
            target_user=target_user,
        )

async def warn_bad_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await manual_warn(update, context, "bad_words")


async def warn_ad_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await manual_warn(update, context, "ads")

async def manual_dwarn(update: Update, context: ContextTypes.DEFAULT_TYPE, reason: str):
    message = update.message

    if not message or message.chat.type not in ["group", "supergroup"]:
        return

    await delete_admin_command(message)

    admin = message.from_user
    lang = get_group_language(message.chat.id)

    if not await is_admin(message.chat, admin.id):
        return

    if not message.reply_to_message:
        msg = await message.chat.send_message(TEXTS[lang]["user_not_found"])
        await asyncio.sleep(3)
        await msg.delete()
        return

    target_user = message.reply_to_message.from_user

    try:
        await message.reply_to_message.delete()
    except Exception as e:
        print("DELETE DWARN MESSAGE ERROR:", e)

    settings = get_group_settings(message.chat.id)

    if reason == "bad_words":
        await handle_warning(
            message=message,
            lang=lang,
            reason="bad_words",
            reason_key="reason_bad_word",
            limit=settings["bad_words_warn_limit"],
            punish_enabled=settings["punish_bad_words"],
            show_warning=True,
            punish_seconds=settings["bad_words_punish_seconds"],
            target_user=target_user,
        )

    elif reason == "ads":
        await handle_warning(
            message=message,
            lang=lang,
            reason="ads",
            reason_key="reason_ads",
            limit=settings["ads_warn_limit"],
            punish_enabled=settings["punish_ads"],
            show_warning=True,
            punish_seconds=settings["ads_punish_seconds"],
            target_user=target_user,
        )

async def dwarn_bad_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await manual_dwarn(update, context, "bad_words")


async def dwarn_ad_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await manual_dwarn(update, context, "ads")

async def apply_kick(message, target_user, lang: str):
    await message.chat.ban_member(
        user_id=target_user.id
    )

    await message.chat.unban_member(
        user_id=target_user.id,
        only_if_banned=True
    )

    msg = await message.chat.send_message(
        TEXTS[lang]["user_kicked"].format(
            name=target_user.first_name
        )
    )

    await asyncio.sleep(3)

    try:
        await msg.delete()
    except Exception as e:
        print("DELETE KICK MESSAGE ERROR:", e)

async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or message.chat.type not in ["group", "supergroup"]:
        return

    await delete_admin_command(message)

    admin = message.from_user
    lang = get_group_language(message.chat.id)

    if not await is_admin(message.chat, admin.id):
        return

    target_user = await resolve_mute_target(message, context, context.args)

    if not target_user:
        msg = await message.chat.send_message(TEXTS[lang]["user_not_found"])
        await asyncio.sleep(3)

        try:
            await msg.delete()
        except Exception as e:
            print("DELETE KICK ERROR MESSAGE ERROR:", e)

        return

    try:
        await apply_kick(message, target_user, lang)

    except Exception as e:
        print("KICK ERROR:", e)

async def dkick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or message.chat.type not in ["group", "supergroup"]:
        return

    await delete_admin_command(message)

    admin = message.from_user
    lang = get_group_language(message.chat.id)

    if not await is_admin(message.chat, admin.id):
        return

    if not message.reply_to_message:
        msg = await message.chat.send_message(TEXTS[lang]["user_not_found"])
        await asyncio.sleep(3)

        try:
            await msg.delete()
        except Exception as e:
            print("DELETE DKICK ERROR MESSAGE ERROR:", e)

        return

    target_user = message.reply_to_message.from_user

    try:
        await message.reply_to_message.delete()
    except Exception as e:
        print("DELETE DKICK TARGET MESSAGE ERROR:", e)

    try:
        await apply_kick(message, target_user, lang)

    except Exception as e:
        print("DKICK ERROR:", e)

async def apply_ban(message, target_user, lang: str):
    await message.chat.ban_member(
        user_id=target_user.id
    )

    msg = await message.chat.send_message(
        TEXTS[lang]["user_banned"].format(
            name=target_user.first_name
        )
    )

    await asyncio.sleep(3)

    try:
        await msg.delete()
    except Exception as e:
        print("DELETE BAN MESSAGE ERROR:", e)

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or message.chat.type not in ["group", "supergroup"]:
        return

    await delete_admin_command(message)

    admin = message.from_user
    lang = get_group_language(message.chat.id)

    if not await is_admin(message.chat, admin.id):
        return

    target_user = await resolve_mute_target(message, context, context.args)

    if not target_user:
        msg = await message.chat.send_message(TEXTS[lang]["user_not_found"])

        await asyncio.sleep(3)

        try:
            await msg.delete()
        except Exception as e:
            print("DELETE BAN ERROR MESSAGE ERROR:", e)

        return

    try:
        await apply_ban(message, target_user, lang)

    except Exception as e:
        print("BAN ERROR:", e)

async def dban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or message.chat.type not in ["group", "supergroup"]:
        return

    await delete_admin_command(message)

    admin = message.from_user
    lang = get_group_language(message.chat.id)

    if not await is_admin(message.chat, admin.id):
        return

    if not message.reply_to_message:
        msg = await message.chat.send_message(TEXTS[lang]["user_not_found"])

        await asyncio.sleep(3)

        try:
            await msg.delete()
        except Exception as e:
            print("DELETE DBAN ERROR MESSAGE ERROR:", e)

        return

    target_user = message.reply_to_message.from_user

    try:
        await message.reply_to_message.delete()
    except Exception as e:
        print("DELETE DBAN TARGET MESSAGE ERROR:", e)

    try:
        await apply_ban(message, target_user, lang)

    except Exception as e:
        print("DBAN ERROR:", e)

async def send_temp_group_message(message, text: str):
    msg = await message.chat.send_message(text)

    await asyncio.sleep(3)

    try:
        await msg.delete()
    except Exception as e:
        print("DELETE TEMP GROUP MESSAGE ERROR:", e)

async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or message.chat.type not in ["group", "supergroup"]:
        return

    await delete_admin_command(message)

    admin = message.from_user
    lang = get_group_language(message.chat.id)

    if not await is_admin(message.chat, admin.id):
        return

    if not context.args:
        await send_temp_group_message(
            message,
            TEXTS[lang]["user_not_found"]
        )
        return

    target_user = await resolve_mute_target(message, context, context.args)

    if not target_user:
        await send_temp_group_message(
            message,
            TEXTS[lang]["user_not_found"]
        )
        return

    try:
        await message.chat.restrict_member(
            user_id=target_user.id,
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

        await send_temp_group_message(
            message,
            TEXTS[lang]["user_unmuted"].format(
                name=target_user.first_name
            )
        )

    except Exception as e:
        print("UNMUTE ERROR:", e)

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or message.chat.type not in ["group", "supergroup"]:
        return

    await delete_admin_command(message)

    admin = message.from_user
    lang = get_group_language(message.chat.id)

    if not await is_admin(message.chat, admin.id):
        return

    if not context.args:
        await send_temp_group_message(
            message,
            TEXTS[lang]["user_not_found"]
        )
        return

    target_user = await resolve_mute_target(message, context, context.args)

    if not target_user:
        await send_temp_group_message(
            message,
            TEXTS[lang]["user_not_found"]
        )
        return

    try:
        await message.chat.unban_member(
            user_id=target_user.id,
            only_if_banned=True
        )

        await send_temp_group_message(
            message,
            TEXTS[lang]["user_unbanned"].format(
                name=target_user.first_name
            )
        )

    except Exception as e:
        print("UNBAN ERROR:", e)

async def guide_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or message.chat.type != "private":
        return

    user_id = message.from_user.id

    if is_private_message_limited(user_id):
        return
        
    lang = get_user_language(user_id)

    await message.reply_text(
        TEXTS[lang]["guide_choose_section"],
        reply_markup=build_guide_menu(lang)
    )

async def guide_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if await check_callback_limit(query):
        return

    await query.answer()

    user_id = query.from_user.id
    lang = get_user_language(user_id)

    section = query.data.split(":")[1]

    if section == "bad_words":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    TEXTS[lang]["back_button"],
                    callback_data="guide:back"
                )
            ]
        ])

        await query.edit_message_text(
            TEXTS[lang]["guide_bad_words_text"],
            parse_mode="HTML",
            reply_markup=keyboard
        )
    elif section == "ads":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    TEXTS[lang]["back_button"],
                    callback_data="guide:back"
                )
            ]
        ])

        await query.edit_message_text(
            TEXTS[lang]["guide_ads_text"],
            parse_mode="HTML",
            reply_markup=keyboard
        )
    elif section == "warnings":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    TEXTS[lang]["back_button"],
                    callback_data="guide:back"
                )
            ]
        ])

        await query.edit_message_text(
            TEXTS[lang]["guide_warnings_text"],
            parse_mode="HTML",
            reply_markup=keyboard
        )
    elif section == "restrictions":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    TEXTS[lang]["back_button"],
                    callback_data="guide:back"
                )
            ]
        ])

        await query.edit_message_text(
            TEXTS[lang]["guide_restrictions_text"],
            parse_mode="HTML",
            reply_markup=keyboard
        )
    elif section == "settings":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    TEXTS[lang]["back_button"],
                    callback_data="guide:back"
                )
            ]
        ])

        await query.edit_message_text(
            TEXTS[lang]["guide_settings_text"],
            parse_mode="HTML",
            reply_markup=keyboard
        )
    elif section == "required_subs":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    TEXTS[lang]["back_button"],
                    callback_data="guide:back"
                )
            ]
        ])
    
        await query.edit_message_text(
            TEXTS[lang]["guide_required_subs_text"],
            parse_mode="HTML",
            reply_markup=keyboard
        )
    elif section == "transfer":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    TEXTS[lang]["back_button"],
                    callback_data="guide:back"
                )
            ]
        ])
    
        await query.edit_message_text(
            TEXTS[lang]["guide_transfer_text"],
            parse_mode="HTML",
            reply_markup=keyboard
        )
    elif section == "back":
        await query.edit_message_text(
            TEXTS[lang]["guide_choose_section"],
            reply_markup=build_guide_menu(lang)
        )

    elif section == "close":
        try:
            await query.message.delete()
        except Exception as e:
            print("DELETE GUIDE MESSAGE ERROR:", e)
            
def build_guide_menu(lang):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_guide_bad_words"],
                callback_data="guide:bad_words"
            ),
            InlineKeyboardButton(
                TEXTS[lang]["btn_guide_ads"],
                callback_data="guide:ads"
            ),
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_guide_warnings"],
                callback_data="guide:warnings"
            ),
            InlineKeyboardButton(
                TEXTS[lang]["btn_guide_restrictions"],
                callback_data="guide:restrictions"
            ),
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_guide_settings"],
                callback_data="guide:settings"
            ),
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_guide_required_subs"],
                callback_data="guide:required_subs"
            ),
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_guide_transfer"],
                callback_data="guide:transfer"
            ),
        ],
        [
            InlineKeyboardButton(
                TEXTS[lang]["btn_guide_plan"],
                callback_data="guide:plan"
            ),
        ],
    ])

async def sync_group_owner(chat, context):
    try:
        admins = await context.bot.get_chat_administrators(chat.id)

        for admin in admins:
            if isinstance(admin, ChatMemberOwner):
                save_group_owner(chat.id, admin.user.id)
                return

    except Exception as e:
        print("SYNC GROUP OWNER ERROR:", e)

async def sync_group_admins(chat, context):
    try:
        admins = await context.bot.get_chat_administrators(chat.id)

        for admin in admins:
            role = "owner" if admin.status == "creator" else "admin"

            save_group_admin(
                chat.id,
                admin.user.id,
                role
            )

    except Exception as e:
        print("SYNC GROUP ADMINS ERROR:", e)

async def required_contacts_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if await check_callback_limit(query):
        return

    data = query.data.split(":")
    chat_id = int(data[1])

    lang = get_group_language(chat_id)

    limit = get_required_contacts_limit(chat_id)
    total_invites = get_required_contacts_total_invites(chat_id)

    await query.edit_message_text(
        TEXTS[lang]["required_contacts_panel"].format(
            limit=limit,
            total_invites=total_invites
        ),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    TEXTS[lang]["btn_required_contacts_limit"],
                    callback_data=f"required_contacts_limit:{chat_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    TEXTS[lang]["btn_required_contacts_reset"],
                    callback_data=f"required_contacts_reset:{chat_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    TEXTS[lang]["back_button"],
                    callback_data=f"group_settings:{chat_id}"
                )
            ]
        ])
    )

async def required_contacts_limit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if await check_callback_limit(query):
        return

    chat_id = int(query.data.split(":")[1])
    lang = get_group_language(chat_id)

    context.user_data["state"] = "setting_required_contacts_limit"
    context.user_data["target_chat_id"] = chat_id

    await query.edit_message_text(
        TEXTS[lang]["required_contacts_enter_limit"],
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    TEXTS[lang]["back_button"],
                    callback_data=f"required_contacts_panel:{chat_id}"
                )
            ]
        ])
    )

async def required_contacts_reset_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if await check_callback_limit(query):
        return

    chat_id = int(query.data.split(":")[1])
    lang = get_group_language(chat_id)

    reset_required_contacts_invites(chat_id)

    await query.answer(TEXTS[lang]["required_contacts_reset_done"], show_alert=True)

    await required_contacts_panel_callback(update, context)

async def check_required_contacts_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    data = query.data.split(":")
    chat_id = int(data[1])
    target_user_id = int(data[2])

    if query.from_user.id != target_user_id:
        await query.answer()
        return

    if not is_group_active(chat_id):
        return

    lang = get_group_language(chat_id)

    limit = get_required_contacts_limit(chat_id)
    added = get_user_required_contacts_count(chat_id, target_user_id)

    if added >= limit:
        try:
            chat = await context.bot.get_chat(chat_id)
    
            await chat.restrict_member(
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
                    can_invite_users=True
                )
            )
    
        except Exception as e:
            print("REQUIRED CONTACTS UNMUTE ERROR:", e)
    
        await query.answer(
            TEXTS[lang]["required_contacts_check_success"],
            show_alert=True
        )
    
        try:
            await query.message.delete()
        except Exception as e:
            print("DELETE REQUIRED CONTACTS CHECK MESSAGE ERROR:", e)
    
        return

    left = limit - added

    await query.answer(
        TEXTS[lang]["required_contacts_check_failed"].format(
            added=added,
            left=left
        ),
        show_alert=True
    )

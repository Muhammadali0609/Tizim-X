from telegram import ChatMemberAdministrator, ChatMemberOwner
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from html import escape
import math
from config import OWNER_ID
from texts import TEXTS
from zoneinfo import ZoneInfo
from db import (get_admin_stats,
    get_admin_groups_page,
    get_admin_groups_count,
    ADMIN_GROUPS_PER_PAGE,
    get_admin_group,
    get_admin_required_subs_count,
    get_admin_required_subs_page,
    ADMIN_REQUIRED_SUBS_PER_PAGE,
    get_group_owner,
    get_admin_users_count,
    get_admin_users_page,
    ADMIN_USERS_PER_PAGE,
)

async def is_admin(chat, user_id: int) -> bool:
    member = await chat.get_member(user_id)

    return isinstance(
        member,
        (
            ChatMemberAdministrator,
            ChatMemberOwner
        )
    )

def build_admin_panel():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                TEXTS["ru"]["btn_admin_stats"],
                callback_data="admin:stats"
            ),
            InlineKeyboardButton(
                TEXTS["ru"]["btn_admin_groups"],
                callback_data="admin:groups"
            ),
        ],
        [
            InlineKeyboardButton(
                TEXTS["ru"]["btn_admin_users"],
                callback_data="admin:users"
            ),
            InlineKeyboardButton(
                TEXTS["ru"]["btn_admin_plans"],
                callback_data="admin:plans"
            ),
        ],
        [
            InlineKeyboardButton(
                TEXTS["ru"]["btn_admin_disabled_groups"],
                callback_data="admin:disabled_groups"
            ),
        ],
        [
            InlineKeyboardButton(
                TEXTS["ru"]["btn_admin_broadcast"],
                callback_data="admin:broadcast"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS["ru"]["btn_admin_close"],
                callback_data="admin:close"
            ),
        ],
    ])


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or message.chat.type != "private":
        return

    user_id = message.from_user.id

    if user_id != OWNER_ID:
        await message.reply_text(
            TEXTS["ru"]["admin_access_denied"]
        )
        return

    await message.reply_text(
        TEXTS["ru"]["admin_panel"],
        reply_markup=build_admin_panel()
    )


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    user_id = query.from_user.id

    if user_id != OWNER_ID:
        await query.answer(
            TEXTS["ru"]["admin_access_denied"],
            show_alert=True
        )
        return

    data = query.data.split(":")[1]

    if data == "close":
        try:
            await query.message.delete()
        except Exception as e:
            print("DELETE ADMIN PANEL ERROR:", e)

        return

    if data == "stats":
        stats = get_admin_stats()
    
        await query.edit_message_text(
            TEXTS["ru"]["admin_stats_text"].format(**stats),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        TEXTS["ru"]["back_button"],
                        callback_data="admin:back"
                    )
                ],
                [
                    InlineKeyboardButton(
                        TEXTS["ru"]["btn_admin_close"],
                        callback_data="admin:close"
                    )
                ]
            ])
        )
        return

    if data == "groups":
        await show_admin_groups(query, 0)
        return

    if data == "users":
        await show_admin_users(query, 0)
        return

    if data == "broadcast":
        broadcast = context.user_data.get("broadcast")
    
        if broadcast:
            context.user_data["admin_state"] = "broadcast_preview"
    
            await query.message.delete()
            await send_broadcast_preview(query.message, broadcast)
            return
    
        context.user_data["admin_state"] = "broadcast_text"
    
        await query.edit_message_text(
            TEXTS["ru"]["admin_broadcast_enter"],
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        TEXTS["ru"]["back_button"],
                        callback_data="admin:back"
                    )
                ],
                [
                    InlineKeyboardButton(
                        TEXTS["ru"]["btn_admin_close"],
                        callback_data="admin:close"
                    )
                ]
            ])
        )
        return
    
    if data == "back":
        await query.edit_message_text(
            TEXTS["ru"]["admin_panel"],
            reply_markup=build_admin_panel()
        )
        return

    await query.answer()

def build_admin_groups_keyboard(page: int, total_pages: int, rows):
    keyboard = []

    number_buttons = []

    for i, (chat_id, _) in enumerate(rows, start=1):
        number_buttons.append(
            InlineKeyboardButton(
                str(i),
                callback_data=f"admin_group:{chat_id}"
            )
        )

    for i in range(0, len(number_buttons), 5):
        keyboard.append(number_buttons[i:i + 5])

    nav = []

    if page > 0:
        nav.append(
            InlineKeyboardButton(
                "⬅️",
                callback_data=f"admin_groups:{page - 1}"
            )
        )

    if page < total_pages - 1:
        nav.append(
            InlineKeyboardButton(
                "➡️",
                callback_data=f"admin_groups:{page + 1}"
            )
        )

    if nav:
        keyboard.append(nav)

    keyboard.append([
        InlineKeyboardButton(
            "🔎 Поиск",
            callback_data="admin_group_search"
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            TEXTS["ru"]["back_button"],
            callback_data="admin:back"
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            TEXTS["ru"]["btn_admin_close"],
            callback_data="admin:close"
        )
    ])

    return InlineKeyboardMarkup(keyboard)

async def show_admin_groups(query, page: int):
    total_count = get_admin_groups_count()

    if total_count == 0:
        await query.edit_message_text(
            TEXTS["ru"]["admin_groups_empty"],
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        TEXTS["ru"]["back_button"],
                        callback_data="admin:back"
                    )
                ],
                [
                    InlineKeyboardButton(
                        TEXTS["ru"]["btn_admin_close"],
                        callback_data="admin:close"
                    )
                ]
            ])
        )
        return

    total_pages = math.ceil(total_count / ADMIN_GROUPS_PER_PAGE)
    page = max(0, min(page, total_pages - 1))

    rows = get_admin_groups_page(page)

    groups_text = "\n".join(
        f"{i + 1 + page * ADMIN_GROUPS_PER_PAGE}. {title}"
        for i, (_, title) in enumerate(rows)
    )

    await query.edit_message_text(
        TEXTS["ru"]["admin_groups_text"].format(
            page=page + 1,
            total_pages=total_pages,
            groups=groups_text
        ),
        parse_mode="HTML",
        reply_markup=build_admin_groups_keyboard(page, total_pages, rows),
        disable_web_page_preview=True
    )

async def admin_groups_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != OWNER_ID:
        await query.answer(TEXTS["ru"]["admin_access_denied"], show_alert=True)
        return

    page = int(query.data.split(":")[1])

    await show_admin_groups(query, page)

def build_admin_group_keyboard(chat_id: int, is_disabled: bool):
    toggle_text = (
        "✅ Включить группу"
        if is_disabled
        else "🚫 Отключить группу"
    )

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💎 Изменить тариф",
                callback_data=f"admin_group_plan:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 Обязательные подписки",
                callback_data=f"admin_group_required_subs:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                toggle_text,
                callback_data=f"admin_group_toggle:{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS["ru"]["back_button"],
                callback_data="admin:groups"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS["ru"]["btn_admin_close"],
                callback_data="admin:close"
            )
        ]
    ])

async def show_admin_group_card(query, chat_id: int):
    group = get_admin_group(chat_id)

    if not group:
        await query.answer("Группа не найдена", show_alert=True)
        return

    (
        group_chat_id,
        title,
        username,
        chat_type,
        language,
        plan_name,
        expires_at,
        is_disabled,
        created_at
    ) = group

    status = (
        TEXTS["ru"]["admin_group_disabled"]
        if is_disabled
        else TEXTS["ru"]["admin_group_active"]
    )

    if expires_at:
        expires_at = (
            expires_at
            .astimezone(ZoneInfo("Asia/Tashkent"))
            .strftime("%d.%m.%Y %H:%M")
        )
    else:
        expires_at = "-"

    if created_at:
        created_at_text = created_at.astimezone(
            ZoneInfo("Asia/Tashkent")
        ).strftime("%d.%m.%Y %H:%M")
    else:
        created_at_text = "-"

    owner_id = get_group_owner(group_chat_id)
    print("ADMIN CARD GROUP ID:", group_chat_id)
    print("ADMIN CARD OWNER ID:", owner_id)

    if owner_id:
        owner = f'<a href="tg://user?id={owner_id}">Владелец</a>'
    else:
        owner = "Неизвестно"

    await query.edit_message_text(
        TEXTS["ru"]["admin_group_text"].format(
            title=title,
            chat_id=group_chat_id,
            username=f"@{username}" if username else "Приватный",
            chat_type=chat_type,
            language=language,
            plan_name=plan_name,
            expires_at=expires_at,
            created_at=created_at_text,
            owner=owner,
            status=status
        ),
        parse_mode="HTML",
        reply_markup=build_admin_group_keyboard(
            group_chat_id,
            is_disabled
        )
    )

async def admin_group_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    user_id = query.from_user.id

    if user_id != OWNER_ID:
        await query.answer(
            TEXTS["ru"]["admin_access_denied"],
            show_alert=True
        )
        return

    chat_id = int(query.data.split(":")[1])

    await show_admin_group_card(query, chat_id)

async def admin_group_search_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != OWNER_ID:
        await query.answer(TEXTS["ru"]["admin_access_denied"], show_alert=True)
        return

    context.user_data["admin_state"] = "searching_group"

    await query.edit_message_text(
        "🔎 Отправьте ID группы.\n\nНапример:\n<code>-1002008044459</code>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    TEXTS["ru"]["back_button"],
                    callback_data="admin:groups"
                )
            ],
            [
                InlineKeyboardButton(
                    TEXTS["ru"]["btn_admin_close"],
                    callback_data="admin:close"
                )
            ]
        ])
    )

async def admin_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or message.chat.type != "private":
        return

    user_id = message.from_user.id

    if user_id != OWNER_ID:
        return

    if context.user_data.get("admin_state") != "searching_group":
        return

    text = message.text.strip()

    if not text.lstrip("-").isdigit():
        await message.reply_text("❌ Неверный ID группы.")
        return

    chat_id = int(text)

    group = get_admin_group(chat_id)

    if not group:
        await message.reply_text("❌ Группа не найдена.")
        return

    context.user_data.pop("admin_state", None)

    await send_admin_group_card(message, chat_id)

async def send_admin_group_card(message, chat_id: int):
    group = get_admin_group(chat_id)

    if not group:
        await message.reply_text("❌ Группа не найдена.")
        return

    (
        group_chat_id,
        title,
        username,
        chat_type,
        language,
        plan_name,
        expires_at,
        is_disabled,
        created_at
    ) = group

    status = (
        TEXTS["ru"]["admin_group_disabled"]
        if is_disabled
        else TEXTS["ru"]["admin_group_active"]
    )

    if expires_at:
        expires_at = expires_at.astimezone(
            ZoneInfo("Asia/Tashkent")
        ).strftime("%d.%m.%Y %H:%M")
    else:
        expires_at = "-"

    if created_at:
        created_at_text = created_at.astimezone(
            ZoneInfo("Asia/Tashkent")
        ).strftime("%d.%m.%Y %H:%M")
    else:
        created_at_text = "-"

    owner_id = get_group_owner(group_chat_id)

    if owner_id:
        owner = f'<a href="tg://user?id={owner_id}">Владелец</a>'
    else:
        owner = "Неизвестно"

    await message.reply_text(
        TEXTS["ru"]["admin_group_text"].format(
            title=title,
            chat_id=group_chat_id,
            username=f"@{username}" if username else "Приватный",
            chat_type=chat_type,
            language=language,
            plan_name=plan_name,
            expires_at=expires_at,
            created_at=created_at_text,
            owner=owner,
            status=status
        ),
        parse_mode="HTML",
        reply_markup=build_admin_group_keyboard(
            group_chat_id,
            is_disabled
        )
    )

def build_admin_required_subs_keyboard(chat_id: int, page: int, total_pages: int):
    keyboard = []

    nav = []

    if page > 0:
        nav.append(
            InlineKeyboardButton(
                "⬅️",
                callback_data=f"admin_group_required_subs:{chat_id}:{page - 1}"
            )
        )

    if page < total_pages - 1:
        nav.append(
            InlineKeyboardButton(
                "➡️",
                callback_data=f"admin_group_required_subs:{chat_id}:{page + 1}"
            )
        )

    if nav:
        keyboard.append(nav)

    keyboard.append([
        InlineKeyboardButton(
            TEXTS["ru"]["back_button"],
            callback_data=f"admin_group:{chat_id}"
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            TEXTS["ru"]["btn_admin_close"],
            callback_data="admin:close"
        )
    ])

    return InlineKeyboardMarkup(keyboard)

async def show_admin_required_subs(query, chat_id: int, page: int = 0):
    group = get_admin_group(chat_id)

    if not group:
        await query.answer("Группа не найдена", show_alert=True)
        return

    title = group[1]

    total_count = get_admin_required_subs_count(chat_id)

    if total_count == 0:
        await query.edit_message_text(
            TEXTS["ru"]["admin_required_subs_empty"],
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        TEXTS["ru"]["back_button"],
                        callback_data=f"admin_group:{chat_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        TEXTS["ru"]["btn_admin_close"],
                        callback_data="admin:close"
                    )
                ]
            ])
        )
        return

    total_pages = math.ceil(total_count / ADMIN_REQUIRED_SUBS_PER_PAGE)
    page = max(0, min(page, total_pages - 1))

    rows = get_admin_required_subs_page(chat_id, page)

    subs_text = "\n".join(
        f"{i + 1 + page * ADMIN_REQUIRED_SUBS_PER_PAGE}. {target_chat}"
        for i, (target_chat, _) in enumerate(rows)
    )

    await query.edit_message_text(
        TEXTS["ru"]["admin_required_subs_text"].format(
            title=title,
            page=page + 1,
            total_pages=total_pages,
            subs=subs_text
        ),
        parse_mode="HTML",
        reply_markup=build_admin_required_subs_keyboard(
            chat_id,
            page,
            total_pages
        )
    )

async def admin_required_subs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != OWNER_ID:
        await query.answer(TEXTS["ru"]["admin_access_denied"], show_alert=True)
        return

    data = query.data.split(":")
    chat_id = int(data[1])
    page = int(data[2]) if len(data) > 2 else 0

    await show_admin_required_subs(query, chat_id, page)

def build_admin_users_keyboard(page: int, total_pages: int, rows):
    keyboard = []

    nav = []

    user_buttons = []

    for i, (user_id, _) in enumerate(rows, start=1):
        user_buttons.append(
            InlineKeyboardButton(
                str(i),
                url=f"tg://user?id={user_id}"
            )
        )
    
    for i in range(0, len(user_buttons), 5):
        keyboard.append(user_buttons[i:i + 5])

    if page > 0:
        nav.append(
            InlineKeyboardButton(
                "⬅️",
                callback_data=f"admin_users:{page - 1}"
            )
        )

    if page < total_pages - 1:
        nav.append(
            InlineKeyboardButton(
                "➡️",
                callback_data=f"admin_users:{page + 1}"
            )
        )

    if nav:
        keyboard.append(nav)

    keyboard.append([
        InlineKeyboardButton(
            TEXTS["ru"]["back_button"],
            callback_data="admin:back"
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            TEXTS["ru"]["btn_admin_close"],
            callback_data="admin:close"
        )
    ])

    return InlineKeyboardMarkup(keyboard)

async def show_admin_users(query, page: int):
    total_count = get_admin_users_count()

    if total_count == 0:
        await query.edit_message_text(
            TEXTS["ru"]["admin_users_empty"],
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        TEXTS["ru"]["back_button"],
                        callback_data="admin:back"
                    )
                ],
                [
                    InlineKeyboardButton(
                        TEXTS["ru"]["btn_admin_close"],
                        callback_data="admin:close"
                    )
                ]
            ])
        )
        return

    total_pages = math.ceil(total_count / ADMIN_USERS_PER_PAGE)

    page = max(0, min(page, total_pages - 1))

    rows = get_admin_users_page(page)

    users_text = "\n".join(
        f"{i + 1 + page * ADMIN_USERS_PER_PAGE}. {escape(str(first_name or user_id))}"
        for i, (user_id, first_name) in enumerate(rows)
    )

    await query.edit_message_text(
        TEXTS["ru"]["admin_users_text"].format(
            page=page + 1,
            total_pages=total_pages,
            users=users_text
        ),
        parse_mode="HTML",
        reply_markup=build_admin_users_keyboard(
            page,
            total_pages,
            rows
        )
    )

async def admin_users_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    user_id = query.from_user.id

    if user_id != OWNER_ID:
        await query.answer(
            TEXTS["ru"]["admin_access_denied"],
            show_alert=True
        )
        return

    page = int(query.data.split(":")[1])

    await show_admin_users(query, page)

def build_broadcast_preview_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                TEXTS["ru"]["btn_broadcast_attach"],
                callback_data="broadcast_attach"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS["ru"]["btn_broadcast_button"],
                callback_data="broadcast_add_button"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS["ru"]["btn_broadcast_send"],
                callback_data="broadcast_send"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS["ru"]["btn_broadcast_cancel"],
                callback_data="broadcast_cancel"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS["ru"]["btn_admin_close"],
                callback_data="admin:close"
            )
        ]
    ])

async def send_broadcast_preview(target, broadcast):
    keyboard = build_broadcast_preview_keyboard()

    buttons = []

    for button in broadcast.get("buttons", []):
        buttons.append([
            InlineKeyboardButton(
                button["text"],
                url=button["url"]
            )
        ])

    if buttons:
        keyboard = InlineKeyboardMarkup(
            buttons + list(keyboard.inline_keyboard)
        )

    text = broadcast.get("text") or TEXTS["ru"]["admin_broadcast_preview"]

    media_type = broadcast.get("media_type")
    file_id = broadcast.get("file_id")

    if media_type == "photo":
        await target.reply_photo(
            photo=file_id,
            caption=text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    elif media_type == "video":
        await target.reply_video(
            video=file_id,
            caption=text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    elif media_type == "animation":
        await target.reply_animation(
            animation=file_id,
            caption=text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    else:
        await target.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

async def broadcast_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != OWNER_ID:
        await query.answer(TEXTS["ru"]["admin_access_denied"], show_alert=True)
        return

    data = query.data

    if data == "broadcast_attach":
        context.user_data["admin_state"] = "broadcast_file"

        await query.message.delete()

        await query.message.chat.send_message(
            TEXTS["ru"]["broadcast_attach_enter"],
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        TEXTS["ru"]["back_button"],
                        callback_data="broadcast_back_preview"
                    )
                ],
                [
                    InlineKeyboardButton(
                        TEXTS["ru"]["btn_admin_close"],
                        callback_data="admin:close"
                    )
                ]
            ])
        )
        return

    if data == "broadcast_add_button":
        context.user_data["admin_state"] = "broadcast_button"

        await query.message.delete()

        await query.message.chat.send_message(
            TEXTS["ru"]["broadcast_button_enter"],
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        TEXTS["ru"]["back_button"],
                        callback_data="broadcast_back_preview"
                    )
                ],
                [
                    InlineKeyboardButton(
                        TEXTS["ru"]["btn_admin_close"],
                        callback_data="admin:close"
                    )
                ]
            ])
        )
        return

    if data == "broadcast_back_preview":
        broadcast = context.user_data.get("broadcast")

        if not broadcast:
            await query.answer("Черновик не найден", show_alert=True)
            return

        await query.message.delete()
        await send_broadcast_preview(query.message, broadcast)
        return

    if data == "broadcast_cancel":
        context.user_data.pop("broadcast", None)
        context.user_data.pop("admin_state", None)

        await query.message.delete()

        await query.message.chat.send_message(
            TEXTS["ru"]["broadcast_cancelled"],
            reply_markup=build_admin_panel()
        )
        return

    if data == "broadcast_send":
        broadcast = context.user_data.get("broadcast")
    
        if not broadcast:
            await query.answer("Черновик не найден", show_alert=True)
            return
    
        await query.message.delete()
    
        await query.message.chat.send_message(
            TEXTS["ru"]["broadcast_choose_target"],
            reply_markup=build_broadcast_target_keyboard()
        )
        return

    if data == "broadcast_target_user":
        context.user_data["admin_state"] = "broadcast_target_user"
    
        await query.message.delete()
    
        await query.message.chat.send_message(
            TEXTS["ru"]["broadcast_enter_user_id"],
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        TEXTS["ru"]["back_button"],
                        callback_data="broadcast_send"
                    )
                ],
                [
                    InlineKeyboardButton(
                        TEXTS["ru"]["btn_admin_close"],
                        callback_data="admin:close"
                    )
                ]
            ])
        )
        return

async def admin_broadcast_file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or message.chat.type != "private":
        return

    user_id = message.from_user.id

    if user_id != OWNER_ID:
        return

    if context.user_data.get("admin_state") != "broadcast_file":
        return

    broadcast = context.user_data.get("broadcast")

    if not broadcast:
        return

    if message.photo:
        broadcast["media_type"] = "photo"
        broadcast["file_id"] = message.photo[-1].file_id

    elif message.video:
        broadcast["media_type"] = "video"
        broadcast["file_id"] = message.video.file_id

    elif message.animation:
        broadcast["media_type"] = "animation"
        broadcast["file_id"] = message.animation.file_id

    else:
        await message.reply_text(TEXTS["ru"]["broadcast_invalid_file"])
        return

    context.user_data["admin_state"] = "broadcast_preview"

    await send_broadcast_preview(message, broadcast)

async def admin_broadcast_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or message.chat.type != "private":
        return

    user_id = message.from_user.id

    if user_id != OWNER_ID:
        return

    state = context.user_data.get("admin_state")

    if state not in ["broadcast_text", "broadcast_button"]:
        return

    if state == "broadcast_text":
        context.user_data["broadcast"] = {
            "text": message.text_html,
            "media_type": None,
            "file_id": None,
            "buttons": []
        }

        context.user_data["admin_state"] = "broadcast_preview"

        await send_broadcast_preview(
            message,
            context.user_data["broadcast"]
        )
        return

    if state == "broadcast_button":
        broadcast = context.user_data.get("broadcast")

        if not broadcast:
            return

        parts = message.text.strip().split("\n", 1)

        if len(parts) != 2:
            await message.reply_text(TEXTS["ru"]["broadcast_invalid_button"])
            return

        button_text = parts[0].strip()
        button_url = parts[1].strip()

        if not button_text or not button_url.startswith(("http://", "https://")):
            await message.reply_text(TEXTS["ru"]["broadcast_invalid_button"])
            return

        broadcast.setdefault("buttons", []).append({
            "text": button_text,
            "url": button_url
        })

        context.user_data["admin_state"] = "broadcast_preview"

        await send_broadcast_preview(message, broadcast)
        return

async def admin_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("admin_state")

    if state == "searching_group":
        await admin_text_handler(update, context)
        return

    if state in ["broadcast_text", "broadcast_button"]:
        await admin_broadcast_input_handler(update, context)
        return

    if state == "broadcast_target_user":
        await admin_broadcast_send_user_handler(update, context)
        return

def build_broadcast_target_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                TEXTS["ru"]["btn_broadcast_to_user"],
                callback_data="broadcast_target_user"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS["ru"]["btn_broadcast_to_all_users"],
                callback_data="broadcast_target_all_users"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS["ru"]["btn_broadcast_to_groups"],
                callback_data="broadcast_target_groups"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS["ru"]["back_button"],
                callback_data="broadcast_back_preview"
            )
        ],
        [
            InlineKeyboardButton(
                TEXTS["ru"]["btn_admin_close"],
                callback_data="admin:close"
            )
        ]
    ])

async def send_broadcast_to_chat(context, chat_id: int, broadcast: dict):
    keyboard = None

    buttons = []

    for button in broadcast.get("buttons", []):
        buttons.append([
            InlineKeyboardButton(
                button["text"],
                url=button["url"]
            )
        ])

    if buttons:
        keyboard = InlineKeyboardMarkup(buttons)

    text = broadcast.get("text") or ""

    media_type = broadcast.get("media_type")
    file_id = broadcast.get("file_id")

    if media_type == "photo":
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=file_id,
            caption=text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    elif media_type == "video":
        await context.bot.send_video(
            chat_id=chat_id,
            video=file_id,
            caption=text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    elif media_type == "animation":
        await context.bot.send_animation(
            chat_id=chat_id,
            animation=file_id,
            caption=text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard,
            disable_web_page_preview=True
        )

async def admin_broadcast_send_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or message.chat.type != "private":
        return

    if message.from_user.id != OWNER_ID:
        return

    text = message.text.strip()

    if not text.isdigit():
        await message.reply_text(TEXTS["ru"]["broadcast_user_id_invalid"])
        return

    target_user_id = int(text)

    broadcast = context.user_data.get("broadcast")

    if not broadcast:
        await message.reply_text("❌ Черновик не найден.")
        return

    try:
        await send_broadcast_to_chat(
            context,
            target_user_id,
            broadcast
        )

        await message.reply_text(
            TEXTS["ru"]["broadcast_user_sent"],
            reply_markup=build_admin_panel()
        )

        context.user_data.pop("broadcast", None)
        context.user_data.pop("admin_state", None)

    except Exception as e:
        print("BROADCAST USER SEND ERROR:", e)

        await message.reply_text(
            TEXTS["ru"]["broadcast_user_send_error"]
        )

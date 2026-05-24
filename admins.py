from telegram import ChatMemberAdministrator, ChatMemberOwner
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
import math
from config import OWNER_ID
from texts import TEXTS
from db import get_admin_stats, get_admin_groups_page, get_admin_groups_count, ADMIN_GROUPS_PER_PAGE


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
        
    if data == "back":
        await query.edit_message_text(
            TEXTS["ru"]["admin_panel"],
            reply_markup=build_admin_panel()
        )
        return

    await query.answer()

def build_admin_groups_keyboard(page: int, total_pages: int):
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

    keyboard = []

    if nav:
        keyboard.append(nav)

    keyboard.append([
        InlineKeyboardButton(
            "🔎 Поиск",
            callback_data="admin_groups_search"
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
        f'{i + 1 + page * ADMIN_GROUPS_PER_PAGE}. '
        f'<a href="https://t.me/c/{str(abs(chat_id))[3:]}">{title}</a>'
        for i, (chat_id, title) in enumerate(rows)
    )

    await query.edit_message_text(
        TEXTS["ru"]["admin_groups_text"].format(
            page=page + 1,
            total_pages=total_pages,
            groups=groups_text
        ),
        parse_mode="HTML",
        reply_markup=build_admin_groups_keyboard(page, total_pages),
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

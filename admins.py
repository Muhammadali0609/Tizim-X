from telegram import ChatMemberAdministrator, ChatMemberOwner


async def is_admin(chat, user_id: int) -> bool:
    member = await chat.get_member(user_id)

    return isinstance(
        member,
        (
            ChatMemberAdministrator,
            ChatMemberOwner
        )
    )

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config import OWNER_ID
from texts import TEXTS


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

    await query.answer()

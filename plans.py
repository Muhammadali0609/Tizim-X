import asyncio
from html import escape
from zoneinfo import ZoneInfo

from texts import TEXTS
from db import (
    get_groups_for_plan_notifications,
    get_group_admin_ids,
    mark_plan_notification_sent,
)


def format_plan_date(dt):
    return dt.astimezone(
        ZoneInfo("Asia/Tashkent")
    ).strftime("%d.%m.%Y %H:%M")

async def notify_group_admins_about_plan(context, group):
    chat_id = group["chat_id"]
    title = escape(group["title"] or str(chat_id))
    expires_at = format_plan_date(group["expires_at"])
    notification_type = group["type"]

    text_key = {
        "3d": "plan_notify_3d",
        "1d": "plan_notify_1d",
        "expired": "plan_notify_expired",
    }.get(notification_type)

    if not text_key:
        return

    admin_ids = get_group_admin_ids(chat_id)

    for admin_id in admin_ids:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=TEXTS["ru"][text_key].format(
                    title=title,
                    expires_at=expires_at
                ),
                parse_mode="HTML"
            )
            await asyncio.sleep(0.1)

        except Exception as e:
            print("PLAN NOTIFY ERROR:", admin_id, e)

    mark_plan_notification_sent(chat_id, notification_type)


async def plan_notifications_loop(app):
    while True:
        try:
            groups = get_groups_for_plan_notifications()

            for group in groups:
                await notify_group_admins_about_plan(app, group)

        except Exception as e:
            print("PLAN NOTIFICATIONS LOOP ERROR:", e)

        await asyncio.sleep(300)

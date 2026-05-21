from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ChatMemberHandler, MessageHandler, filters
from telegram import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats
from config import BOT_TOKEN, WEBHOOK_URL, PORT
from handlers import (start_command,
    language_callback,
    bot_added_to_group,
    check_group_message,
    set_group_language,
    new_member_handler,
    check_subscription_callback,
    clean_service_message,
    settings_button_handler,
    group_settings_callback,
    back_groups_callback
)
from db import setup_database

async def setup_commands(app):
    await app.bot.set_my_commands(
        [
            BotCommand("start", "Open TizimX"),
        ],
        scope=BotCommandScopeAllPrivateChats()
    )
    await app.bot.set_my_commands(
        [
            BotCommand("ru", "Язык группы русский"),
            BotCommand("uz", "Guruh tili o‘zbekcha"),
        ],
        scope=BotCommandScopeAllGroupChats()
    )

def main():
    setup_database()
    app = Application.builder().token(BOT_TOKEN).build()
    app.post_init = setup_commands

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    app.add_handler(ChatMemberHandler(bot_added_to_group, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, clean_service_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_TITLE, clean_service_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_PHOTO, clean_service_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.DELETE_CHAT_PHOTO, clean_service_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.PINNED_MESSAGE, clean_service_message))
    app.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_sub:"))
    app.add_handler(MessageHandler(filters.Regex("^(⚙️ Управлять|⚙️ Boshqarish)$"), settings_button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_group_message))
    app.add_handler(CommandHandler("ru", set_group_language))
    app.add_handler(CommandHandler("uz", set_group_language))
    app.add_handler(CallbackQueryHandler(group_settings_callback, pattern="^group_settings:"))
    app.add_handler(CallbackQueryHandler(back_groups_callback, pattern="^back_groups$"))
    app.add_handler(CallbackQueryHandler(bad_words_panel_callback, pattern="^bad_words_panel:"))
    app.add_handler(CallbackQueryHandler(bad_words_panel_callback, pattern="^bad_words_page:"))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook",
    )

if __name__ == "__main__":
    main()

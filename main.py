from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ChatMemberHandler

from config import BOT_TOKEN, WEBHOOK_URL, PORT
from handlers import start_command, language_callback, bot_added_to_group
from db import setup_database


def main():
    setup_database()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    app.add_handler(
        ChatMemberHandler(
            bot_added_to_group,
            ChatMemberHandler.MY_CHAT_MEMBER
        )
    )

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook",
    )

if __name__ == "__main__":
    main()

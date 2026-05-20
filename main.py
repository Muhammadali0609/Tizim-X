from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ChatMemberHandler, MessageHandler, filters
from telegram import BotCommand
from config import BOT_TOKEN, WEBHOOK_URL, PORT
from handlers import start_command, language_callback, bot_added_to_group, check_group_message, set_group_language
from db import setup_database

async def setup_commands(app):
    commands = [
        BotCommand("ru", "Русский язык группы"),
        BotCommand("uz", "Guruh tili o‘zbekcha"),
    ]

    await app.bot.set_my_commands(commands)

def main():
    setup_database()
    app = Application.builder().token(BOT_TOKEN).build()
    app.post_init = setup_commands

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    app.add_handler(ChatMemberHandler(bot_added_to_group, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_group_message))
    app.add_handler(CommandHandler("ru", set_group_language))
    app.add_handler(CommandHandler("uz", set_group_language))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook",
    )

if __name__ == "__main__":
    main()

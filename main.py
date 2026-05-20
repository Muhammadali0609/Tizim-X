from telegram.ext import Application, CommandHandler

from config import BOT_TOKEN, WEBHOOK_URL, PORT
from handlers import start_command


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"{WEBHOOK_URL}/webhook",
        secret_token=BOT_TOKEN,
    )


if __name__ == "__main__":
    main()

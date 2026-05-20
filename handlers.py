from telegram import Update
from telegram.ext import ContextTypes

from texts import TEXTS


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXTS["ru"]["start"])

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
    back_groups_callback,
    bad_words_panel_callback,
    add_bad_word_callback,
    private_text_handler,
    ads_panel_callback,
    ads_toggle_links_callback,
    ad_links_panel_callback,
    add_ad_link_callback,
    bad_words_search_callback,
    delete_bad_word_callback,
    ad_phrases_panel_callback,
    add_ad_phrase_callback,
    delete_ad_link_start_callback,
    delete_ad_phrase_start_callback,
    ad_exceptions_panel_callback,
    add_ad_exception_callback,
    delete_ad_exception_start_callback,
    warnings_panel_callback,
    warnings_toggle_callback,
    warnings_limit_callback,
    warnings_set_limit_callback,
    restrictions_panel_callback,
    restrictions_toggle_callback,
    restrictions_duration_callback,
    settings_panel_callback,
    settings_toggle_callback,
    required_subs_panel_callback,
    required_subs_toggle_callback,
    add_required_sub_callback,
    delete_required_sub_start_callback,
    transfer_panel_callback,
    transfer_toggle_callback,
    transfer_all_callback,
    transfer_selected_callback,
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
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND, private_text_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_group_message))
    app.add_handler(CommandHandler("ru", set_group_language))
    app.add_handler(CommandHandler("uz", set_group_language))
    app.add_handler(CallbackQueryHandler(group_settings_callback, pattern="^group_settings:"))
    app.add_handler(CallbackQueryHandler(back_groups_callback, pattern="^back_groups$"))
    app.add_handler(CallbackQueryHandler(bad_words_panel_callback, pattern="^bad_words_panel:"))
    app.add_handler(CallbackQueryHandler(bad_words_panel_callback, pattern="^bad_words_page:"))
    app.add_handler(CallbackQueryHandler(add_bad_word_callback, pattern="^bad_words_add:"))
    app.add_handler(CallbackQueryHandler(ads_panel_callback, pattern="^ads_panel:"))
    app.add_handler(CallbackQueryHandler(ads_toggle_links_callback, pattern="^ads_toggle_links:"))
    app.add_handler(CallbackQueryHandler(ad_links_panel_callback, pattern="^ad_links_panel:"))
    app.add_handler(CallbackQueryHandler(ad_links_panel_callback, pattern="^ad_links_page:"))
    app.add_handler(CallbackQueryHandler(add_ad_link_callback, pattern="^ad_links_add:"))
    app.add_handler(CallbackQueryHandler(bad_words_search_callback, pattern="^bad_words_search:"))
    app.add_handler(CallbackQueryHandler(delete_bad_word_callback, pattern="^delete_bad_word:"))
    app.add_handler(CallbackQueryHandler(ad_phrases_panel_callback, pattern="^ad_phrases_panel:"))
    app.add_handler(CallbackQueryHandler(ad_phrases_panel_callback, pattern="^ad_phrases_page:"))   
    app.add_handler(CallbackQueryHandler(add_ad_phrase_callback, pattern="^ad_phrases_add:"))
    app.add_handler(CallbackQueryHandler(delete_ad_link_start_callback, pattern="^ad_links_delete:"))
    app.add_handler(CallbackQueryHandler(delete_ad_phrase_start_callback, pattern="^ad_phrases_delete:"))
    app.add_handler(CallbackQueryHandler(ad_exceptions_panel_callback, pattern="^ad_exceptions_panel:"))
    app.add_handler(CallbackQueryHandler(ad_exceptions_panel_callback, pattern="^ad_exceptions_page:"))
    app.add_handler(CallbackQueryHandler(add_ad_exception_callback, pattern="^ad_exceptions_add:"))
    app.add_handler(CallbackQueryHandler(delete_ad_exception_start_callback, pattern="^ad_exceptions_delete:"))
    app.add_handler(CallbackQueryHandler(warnings_panel_callback, pattern="^warnings_panel:"))
    app.add_handler(CallbackQueryHandler(warnings_toggle_callback, pattern="^warnings_toggle:"))
    app.add_handler(CallbackQueryHandler(warnings_limit_callback, pattern="^warnings_limit:"))
    app.add_handler(CallbackQueryHandler(warnings_set_limit_callback, pattern="^warnings_set_limit:"))
    app.add_handler(CallbackQueryHandler(restrictions_panel_callback, pattern="^restrictions_panel:"))
    app.add_handler(CallbackQueryHandler(restrictions_toggle_callback, pattern="^restrictions_toggle:"))
    app.add_handler(CallbackQueryHandler(restrictions_duration_callback, pattern="^restrictions_duration:"))
    app.add_handler(CallbackQueryHandler(settings_panel_callback, pattern="^settings_panel:"))
    app.add_handler(CallbackQueryHandler(settings_toggle_callback, pattern="^settings_toggle:"))
    app.add_handler(CallbackQueryHandler(required_subs_panel_callback, pattern="^required_subs_panel:"))
    app.add_handler(CallbackQueryHandler(required_subs_toggle_callback, pattern="^required_subs_toggle:"))
    app.add_handler(CallbackQueryHandler(add_required_sub_callback, pattern="^required_subs_add:"))
    app.add_handler(CallbackQueryHandler(delete_required_sub_start_callback, pattern="^required_subs_delete:"))
    app.add_handler(CallbackQueryHandler(transfer_panel_callback, pattern="^transfer_panel:"))
    app.add_handler(CallbackQueryHandler(transfer_toggle_callback, pattern="^transfer_toggle:"))
    app.add_handler(CallbackQueryHandler(transfer_all_callback, pattern="^transfer_all:"))
    app.add_handler(CallbackQueryHandler(transfer_selected_callback, pattern="^transfer_selected:"))
    
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook",
    )

if __name__ == "__main__":
    main()

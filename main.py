from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ChatMemberHandler, MessageHandler, filters
from telegram.ext import ContextTypes
from telegram import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats, Update
from config import BOT_TOKEN, WEBHOOK_URL, PORT
import asyncio
from handlers import (start_command,
    left_member_handler,
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
    transfer_target_callback,
    transfer_confirm_callback,
    group_plan_callback,
    mute_command,
    dmute_command,
    warn_bad_command,
    warn_ad_command,
    dwarn_bad_command,
    dwarn_ad_command,
    kick_command,
    dkick_command,
    ban_command,
    dban_command,
    unmute_command,
    unban_command,
    language_toggle_handler,
    guide_button_handler,
    guide_callback,
    required_contacts_panel_callback,
    required_contacts_limit_callback,
    required_contacts_reset_callback,
    check_required_contacts_callback,
    required_contacts_reset_confirm_callback,
    auto_responder_panel_callback,
    custom_replies_panel_callback,
    auto_reply_card_callback,
    auto_reply_add_callback,
    auto_reply_draft_callback,
    auto_reply_edit_callback,
    auto_reply_delete_callback,
    auto_delivery_panel_callback,
    auto_material_card_callback,
    auto_material_add_callback,
    auto_material_edit_callback,
    auto_material_delete_callback,
    channel_create_post_callback,
    channel_post_draft_callback,
    channel_post_media_handler,
    channel_post_confirm_send_callback,
    scheduled_channel_posts_loop,
    scheduled_posts_panel_callback,
    scheduled_post_card_callback,
    scheduled_post_change_time_callback,
    scheduled_post_delete_confirm_callback,
    scheduled_post_delete_callback,
    test_payment_command
)
from db import setup_database
from admins import (
    admin_command,
    admin_callback,
    admin_groups_page_callback,
    admin_group_callback,
    admin_group_search_callback,
    admin_required_subs_callback,
    admin_users_page_callback,
    broadcast_callback,
    admin_broadcast_file_handler,
    admin_input_handler,
)
from plans import plan_notifications_loop

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
    
async def private_router_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_state = context.user_data.get("admin_state")

    if admin_state in [
        "searching_group",
        "broadcast_text",
        "broadcast_button",
        "broadcast_target_user",
    ]:
        await admin_input_handler(update, context)
        return

    await private_text_handler(update, context)

def main():
    setup_database()
    app = Application.builder().token(BOT_TOKEN).build()
    async def post_init(app):
        await setup_commands(app)
        asyncio.create_task(plan_notifications_loop(app))
        asyncio.create_task(scheduled_channel_posts_loop(app))
    app.post_init = post_init

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("testpay", test_payment_command))
    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    app.add_handler(ChatMemberHandler(bot_added_to_group, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, left_member_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_TITLE, clean_service_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_PHOTO, clean_service_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.DELETE_CHAT_PHOTO, clean_service_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.PINNED_MESSAGE, clean_service_message))
    app.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_sub:"))
    app.add_handler(CallbackQueryHandler(check_required_contacts_callback, pattern="^check_required_contacts:"))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.Regex("^(⚙️ Управлять|⚙️ Boshqarish)$"), settings_button_handler))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.Regex("^(🌐 Язык|🌐 Til)$"), language_toggle_handler))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.Regex("^(📘 Инструкция|📘 Qo‘llanma)$"), guide_button_handler))
    
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & (filters.PHOTO | filters.VIDEO | filters.ANIMATION), channel_post_media_handler))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & (filters.PHOTO | filters.VIDEO | filters.ANIMATION), admin_broadcast_file_handler))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND, private_router_handler))
    app.add_handler(CommandHandler("mute", mute_command))
    app.add_handler(CommandHandler("dmute", dmute_command))
    app.add_handler(CommandHandler("ru", set_group_language))
    app.add_handler(CommandHandler("uz", set_group_language))
    app.add_handler(CommandHandler("warnbad", warn_bad_command))
    app.add_handler(CommandHandler("warnad", warn_ad_command))
    app.add_handler(CommandHandler("dwarnbad", dwarn_bad_command))
    app.add_handler(CommandHandler("dwarnad", dwarn_ad_command))
    app.add_handler(CommandHandler("kick", kick_command))
    app.add_handler(CommandHandler("dkick", dkick_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("dban", dban_command))
    app.add_handler(CommandHandler("unmute", unmute_command))
    app.add_handler(CommandHandler("unban", unban_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_group_message))
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
    app.add_handler(CallbackQueryHandler(transfer_target_callback, pattern="^transfer_target:"))
    app.add_handler(CallbackQueryHandler(transfer_confirm_callback, pattern="^transfer_confirm:"))
    app.add_handler(CallbackQueryHandler(group_plan_callback, pattern="^group_plan:"))
    app.add_handler(CallbackQueryHandler(guide_callback, pattern="^guide:"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin:"))
    app.add_handler(CallbackQueryHandler(admin_groups_page_callback, pattern="^admin_groups:"))
    app.add_handler(CallbackQueryHandler(admin_required_subs_callback, pattern="^admin_group_required_subs:"))
    app.add_handler(CallbackQueryHandler(admin_group_search_callback, pattern="^admin_group_search$"))
    app.add_handler(CallbackQueryHandler(admin_group_callback, pattern="^admin_group"))
    app.add_handler(CallbackQueryHandler(admin_users_page_callback, pattern="^admin_users:"))
    app.add_handler(CallbackQueryHandler(broadcast_callback, pattern="^broadcast_"))
    app.add_handler(CallbackQueryHandler(required_contacts_panel_callback, pattern="^required_contacts_panel:"))
    app.add_handler(CallbackQueryHandler(required_contacts_limit_callback, pattern="^required_contacts_limit:"))
    app.add_handler(CallbackQueryHandler(required_contacts_reset_confirm_callback, pattern="^required_contacts_reset_confirm:"))
    app.add_handler(CallbackQueryHandler(required_contacts_reset_callback, pattern="^required_contacts_reset:"))
    app.add_handler(CallbackQueryHandler(auto_responder_panel_callback, pattern="^auto_responder_panel:"))
    app.add_handler(CallbackQueryHandler(custom_replies_panel_callback, pattern="^custom_replies_panel:"))
    app.add_handler(CallbackQueryHandler(auto_reply_card_callback, pattern="^auto_reply_card:"))
    app.add_handler(CallbackQueryHandler(auto_reply_add_callback, pattern="^auto_reply_add:"))
    app.add_handler(CallbackQueryHandler(auto_reply_draft_callback, pattern="^auto_reply_draft_"))
    app.add_handler(CallbackQueryHandler(auto_reply_edit_callback, pattern="^auto_reply_edit:"))
    app.add_handler(CallbackQueryHandler(auto_reply_delete_callback, pattern="^auto_reply_delete:"))
    app.add_handler(CallbackQueryHandler(auto_delivery_panel_callback, pattern="^auto_delivery_panel:"))
    app.add_handler(CallbackQueryHandler(auto_material_card_callback, pattern="^auto_material_card:"))
    app.add_handler(CallbackQueryHandler(auto_material_add_callback, pattern="^auto_material_add:"))
    app.add_handler(CallbackQueryHandler(auto_material_edit_callback, pattern="^auto_material_edit:"))
    app.add_handler(CallbackQueryHandler(auto_material_delete_callback, pattern="^auto_material_delete:"))
    app.add_handler(CallbackQueryHandler(channel_create_post_callback, pattern="^channel_create_post:"))
    app.add_handler(CallbackQueryHandler(channel_post_confirm_send_callback, pattern="^channel_post_confirm_send$"))
    app.add_handler(CallbackQueryHandler(channel_post_draft_callback, pattern="^channel_post_"))
    app.add_handler(CallbackQueryHandler(scheduled_posts_panel_callback, pattern="^scheduled_posts_panel:"))
    app.add_handler(CallbackQueryHandler(scheduled_post_card_callback, pattern="^scheduled_post_card:"))
    app.add_handler(CallbackQueryHandler(scheduled_post_change_time_callback, pattern="^scheduled_post_change_time:"))
    app.add_handler(CallbackQueryHandler(scheduled_post_delete_confirm_callback, pattern="^scheduled_post_delete_confirm:"))
    app.add_handler(CallbackQueryHandler(scheduled_post_delete_callback, pattern="^scheduled_post_delete:"))
    
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook",
    )

if __name__ == "__main__":
    main()

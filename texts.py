TEXTS = {
    "ru": {
        "admin_panel": "👑 Админка TizimX\n\nВыберите раздел:",
        "btn_admin_stats": "📊 Статистика",
        "btn_admin_groups": "👥 Группы",
        "btn_admin_users": "👤 Пользователи",
        "btn_admin_plans": "💎 Планы",
        "btn_admin_disabled_groups": "🚫 Отключённые группы",
        "btn_admin_close": "❌ Закрыть",
        "admin_access_denied": "❌ Доступ запрещён.",

        "admin_stats_text": (
            "📊 <b>Статистика TizimX</b>\n\n"
        
            "👤 <b>Пользователи</b>\n"
            "Сегодня: {users_today}\n"
            "7 дней: {users_week}\n"
            "30 дней: {users_month}\n"
            "Всего: {users_total}\n\n"
        
            "👥 <b>Группы</b>\n"
            "Сегодня: {groups_today}\n"
            "7 дней: {groups_week}\n"
            "30 дней: {groups_month}\n"
            "Всего: {groups_total}\n\n"
        
            "📢 <b>Каналы</b>\n"
            "Сегодня: {channels_today}\n"
            "7 дней: {channels_week}\n"
            "30 дней: {channels_month}\n"
            "Всего: {channels_total}"
        ),

        "admin_groups_text": (
            "👥 <b>Группы</b>\n\n"
            "Страница: {page}/{total_pages}\n\n"
            "{groups}"
        ),
        "admin_groups_empty": "👥 Групп пока нет.",

        "admin_group_text": (
            "👥 <b>Карточка группы</b>\n\n"
        
            "Название:\n"
            "{title}\n\n"
        
            "ID:\n"
            "<code>{chat_id}</code>\n\n"

            "Username:\n"
            "{username}\n\n"
        
            "Тип:\n"
            "{chat_type}\n\n"
        
            "Язык:\n"
            "{language}\n\n"
        
            "Тариф:\n"
            "{plan_name}\n\n"
        
            "Действует до:\n"
            "{expires_at}\n\n"
        
            "Статус:\n"
            "{status}"
        ),
        "admin_group_active": "✅ Активна",
        "admin_group_disabled": "🚫 Отключена",
        
        "start": (
            "Добро пожаловать в TizimX.\n\n"
            "TizimX — это система автоматической модерации и управления Telegram-группами.\n\n"
            "Бот помогает автоматически контролировать:\n"
            "<b>• мат и оскорбления</b>\n"
            "<b>• рекламу и ссылки</b>\n"
            "<b>• предупреждения и ограничения</b>\n"
            "<b>• обязательные подписки</b>\n"
            "<b>• ручную модерацию участников</b>\n"
            "<b>• и многое другое</b>\n\n"
            "Добавьте бота в группу и выдайте права администратора для полноценной работы.\n\n"
            "Подробная информация и инструкции доступны в разделе «📘 Инструкция»."
        ),
        "choose_language": "🌐 Выберите язык:",
        "language_saved": "✅ Язык сохранён: Русский",
        "group_connected": (
            "✅ TizimX подключён к группе."
        ),
        "no_admin_rights": (
            "Для работы модерации выдайте боту права администратора."
        ),
        "group_language_ru": "✅ Язык группы изменён на русский.",
        "group_language_uz": "✅ Язык группы изменён на узбекский.",
        "private_welcome": "🛡 Добро пожаловать в TizimX",
        "manage_button": "⚙️ Управлять",
        "language_button": "🌐 Язык",
        "guide_button": "📘 Инструкция",
        "back_button": "⬅️ Назад",
        "choose_group": "📂 Выберите группу:",
        "no_groups": "❌ У вас пока нет подключённых групп.",
        "group_panel": (
            "⚙️ Настройки группы:\n\n"
            "{title}\n\n"
            "ID группы:\n"
            "<code>{chat_id}</code>"
        ),
        "access_denied": "❌ У вас больше нет доступа к этой группе.",
        "enabled": "🟢",
        "disabled": "🔴",

        "required_sub_join_text": (
            "🔒 {name}, чтобы писать в группе, "
            "подпишитесь на следующие:"
        ),
        "required_sub_check_button": "✅ Проверить",
        "required_sub_not_all": "❌ Вы подписались не на все каналы и группы",
        "required_sub_success": "✅ Подписка подтверждена",

        "btn_bad_words": "🤬 Маты",
        "btn_ads": "🚫 Рекламы",
        "btn_warnings": "⚠️ Предупреждения",
        "btn_restrictions": "🔒 Ограничения",
        "btn_settings": "⚙️ Настройки",
        "btn_transfer_settings": "🔁 Перенос настроек",

        "bad_words_title": "🤬 Маты\n\n{words}\n\nСтраница {page}/{total_pages}",
        "bad_words_empty": "🤬 Список матов пуст.",
        "btn_prev": "⬅️ Назад",
        "btn_next": "Вперёд ➡️",
        "btn_search": "🔍 Поиск",
        "btn_back_panel": "⬅️ В меню",

        "btn_add_bad_word": "➕ Добавить мат",
        "add_bad_word_prompt": "✍️ Введите новый мат.\n\nМожно сразу несколько слов, например:\nмат1 мат2 мат3",
        "bad_words_added": "✅ Мат добавлен в группу.",

        "ads_panel": "🚫 Реклама\n\nБлокировка ссылок: {status}",
        "links_enabled": "🟢 Включена",
        "links_disabled": "🔴 Выключена",
        "btn_disable_links": "🔴 Выключить блокировку ссылок",
        "btn_enable_links": "🟢 Включить блокировку ссылок",
        "btn_other_links": "🔗 Другие ссылки",
        "btn_ad_phrases": "💬 Рекламные фразы",
        "btn_ad_exceptions": "✅ Исключения",

        "ad_links_title": "🔗 Другие ссылки\n\n{links}\n\nСтраница {page}/{total_pages}",
        "ad_links_empty": "🔗 Список ссылок пуст.",
        "btn_add_ad_link": "➕ Добавить ссылку",
        "add_ad_link_prompt": "✍️ Введите ссылку.",
        "ad_links_added": "✅ Ссылка добавлена в группу.",

        "bad_word_search_prompt": "🔍 Введите число или мат, например:\n38 или мат2",
        "bad_word_not_found": "❌ Такой мат не существует, можете добавить его.",
        "bad_word_found": "✅ Найдено:\n\n{index}. {word}",
        "btn_delete": "🗑 Удалить",
        "bad_word_deleted": "✅ Мат удалён.",

        "ad_phrases_title": "💬 Рекламные фразы\n\n{phrases}\n\nСтраница {page}/{total_pages}",
        "ad_phrases_empty": "💬 Список рекламных фраз пуст.",
        "btn_add_ad_phrase": "➕ Добавить фразу",
        "add_ad_phrase_prompt": "✍️ Введите рекламную фразу.",
        "ad_phrase_added": "✅ Рекламная фраза добавлена.",

        "btn_delete_ad_link": "🗑 Удалить ссылку",
        "delete_ad_link_prompt": "🗑 Введите номер ссылки для удаления.",
        "ad_link_deleted": "✅ Ссылка удалена.",
        "ad_link_not_found": "❌ Такой ссылки нет.",
        
        "btn_delete_ad_phrase": "🗑 Удалить фразу",
        "delete_ad_phrase_prompt": "🗑 Введите номер фразы для удаления.",
        "ad_phrase_deleted": "✅ Фраза удалена.",
        "ad_phrase_not_found": "❌ Такой фразы нет.",

        "ad_exceptions_title": "✅ Исключения\n\n{exceptions}\n\nСтраница {page}/{total_pages}",
        "ad_exceptions_empty": "✅ Список исключений пуст.",
        "btn_add_ad_exception": "➕ Добавить исключение",
        "btn_delete_ad_exception": "🗑 Удалить исключение",
        "add_ad_exception_prompt": "✍️ Введите исключение.",
        "ad_exception_added": "✅ Исключение добавлено.",
        "delete_ad_exception_prompt": "🗑 Введите номер исключения для удаления.",
        "ad_exception_deleted": "✅ Исключение удалено.",
        "ad_exception_not_found": "❌ Такого исключения нет.",

        "warnings_panel": (
            "⚠️ Предупреждения\n\n"
            "Предупреждение за мат:\n{bad_words_status}\n\n"
            "Предупреждение за рекламу:\n{ads_status}"
        ),
        
        "warn_enabled": "🟢 ВКЛ",
        "warn_disabled": "🔴 ОТКЛ",
        
        "btn_warn_bad_words_on": "🟢 Включить предупреждение за мат",
        "btn_warn_bad_words_off": "🔴 Выключить предупреждение за мат",
        
        "btn_warn_ads_on": "🟢 Включить предупреждение за рекламу",
        "btn_warn_ads_off": "🔴 Выключить предупреждение за рекламу",
        
        "btn_bad_words_warn_limit": "🤬 Число предупреждений за мат: {limit}",
        "btn_ads_warn_limit": "🚫 Число предупреждений за рекламу: {limit}",
        "choose_warn_limit": "⚠️ Выберите число предупреждений:",
        "warn_limit_saved": "✅ Число предупреждений сохранено.",

        "warning_message": (
            "⚠️ {name}, нарушение правил группы.\n\n"
            "Причина: {reason}\n"
            "Предупреждение: {count}/{limit}"
        ),
        "reason_bad_word": "запрещенное слово",
        "reason_ads": "реклама",
        "limit_reached": (
            "🔒 {name} получил ограничение.\n\n"
            "Срок: {duration}\n"
            "Причина: {reason}"
        ),
        "restrictions_panel": (
            "🔒 Ограничения\n\n"
            "Ограничение за мат:\n{bad_words_status}\n"
            "Ограничение за рекламу:\n{ads_status}\n\n"
            "Срок ограничения за мат:\n🕓 {bad_words_duration}\n"
            "Срок ограничения за рекламу:\n🕓 {ads_duration}"
        ),
        "btn_punish_bad_words_on": "🟢 Включить ограничение за мат",
        "btn_punish_bad_words_off": "🔴 Выключить ограничение за мат",
        "btn_punish_ads_on": "🟢 Включить ограничение за рекламу",
        "btn_punish_ads_off": "🔴 Выключить ограничение за рекламу",
        "btn_bad_words_punish_duration": "⏳ Срок за мат",
        "btn_ads_punish_duration": "⏳ Срок за рекламу",

        "enter_duration_prompt": (
            "⏳ Введите срок ограничения.\n\n"
            "Примеры:\n"
            "30m = 30 минут\n"
            "12h = 12 часов\n"
            "7d = 7 дней\n"
            "2d 5h = 2 дня 5 часов\n"
            "1mo = 1 месяц\n"
            "Макс. срок - 12 месяцев\n"
            "Мин. срок - 1 минут\n\n"
            "Бан = забанить\n"
            "Навсегда = мутить навсегда"
        ),
        "invalid_duration_format": (
            "❌ Такой формат не поддерживается.\n\n"
            "Примеры:\n"
            "30m = 30 минут\n"
            "12h = 12 часов\n"
            "7d = 7 дней\n"
            "2d 5h = 2 дня 5 часов\n"
            "1mo = 1 месяц\n"
            "Макс. срок - 12 месяцев\n"
            "Мин. срок - 1 минут\n\n"
            "Бан = забанить\n"
            "Навсегда = мутить навсегда"
        ),
        "duration_saved": "✅ Срок ограничения сохранён.",
        "btn_open_section": "↩️ Открыть раздел",

        "settings_panel": (
            "⚙️ Настройки\n\n"
            "Удаление матов:\n{bad_words_status}\n\n"
            "Удаление рекламы:\n{ads_status}\n\n"
            "Удаление @username:\n{usernames_status}"
        ),
        
        "btn_toggle_bad_words_on": "🟢 Включить удаление матов",
        "btn_toggle_bad_words_off": "🔴 Выключить удаление матов",
        
        "btn_toggle_ads_on": "🟢 Включить удаление рекламы",
        "btn_toggle_ads_off": "🔴 Выключить удаление рекламы",
        
        "btn_toggle_usernames_on": "🟢 Включить удаление @username",
        "btn_toggle_usernames_off": "🔴 Выключить удаление @username",

        "btn_required_subs": "📌 Обязательные подписки",
        "required_subs_panel": (
            "📌 Обязательные подписки\n\n"
            "Статус: {status}\n\n"
            "Список:\n{subs}"
        ),
        "required_subs_empty": "Пока пусто.",
        "btn_required_subs_on": "🟢 Включить обязательные подписки",
        "btn_required_subs_off": "🔴 Выключить обязательные подписки",
        "btn_add_required_sub": "➕ Добавить подписку",
        "btn_delete_required_sub": "🗑 Удалить подписку",

        "add_required_sub_prompt": (
            "➕ Отправьте канал или группу для обязательной подписки.\n\n"
            "Можно отправить:\n"
            "• @username\n"
            "• https://t.me/"
        ),
        "required_sub_added": "✅ Подписка добавлена.",
        "delete_required_sub_prompt": "🗑 Введите номер подписки для удаления.",
        "required_sub_deleted": "✅ Подписка удалена.",
        "required_sub_not_found": "❌ Такой подписки нет.",

        "required_sub_invalid": (
            "❌ Неверный канал или группа.\n\n"
            "Отправьте в формате:\n"
            "• @username\n"
            "или\n"
            "• https://t.me/"
        ),
        "required_sub_not_accessible": (
            "❌ Не удалось найти этот канал или группу.\n\n"
            "Проверьте username или добавьте бота туда админом."
        ),
        "required_subs_empty_alert": "❌ Чтобы включить обязательные подписки, сначала добавьте хотя бы одну подписку.",

        "transfer_panel": (
            "🔁 Перенос настроек\n\n"
            "Выберите настройки и данные, которые хотите перенести."
        ),
        "btn_transfer_bad_words": "Словарь матов: {status}",
        "btn_transfer_ads": "Список реклам: {status}",
        "btn_transfer_warnings": "Предупреждения и лимиты: {status}",
        "btn_transfer_restrictions": "Ограничения и сроки: {status}",
        "btn_transfer_delete_settings": "Настройки удаления: {status}",
        "btn_transfer_all": "🌟 Все настройки",
        "btn_transfer_selected": "🚀 Перенести выбранные",
        "transfer_nothing_selected": "❌ Для переноса выберите хотя бы один пункт.",
        "transfer_choose_group": "📂 Выберите группу, куда перенести настройки:",
        "transfer_no_target_groups": "❌ Нет другой доступной группы для переноса.",

        "transfer_confirm_text": (
            "⚠️ Подтвердите перенос настроек\n\n"
            "Из группы:\n{source_title}\n\n"
            "В группу:\n{target_title}\n\n"
            "Будет перенесено:\n{items}"
        ),
        "btn_confirm": "✅ Подтвердить",
        
        "transfer_item_bad_words": "• Словарь матов",
        "transfer_item_ads": "• Список реклам",
        "transfer_item_warnings": "• Предупреждения и лимиты",
        "transfer_item_restrictions": "• Ограничения и сроки",
        "transfer_item_delete_settings": "• Настройки удаления",
        "transfer_done": "✅ Настройки успешно перенесены.",

        "btn_group_plan": "💎 План группы",
        "group_plan_text": (
            "💎 План группы\n\n"
            "Текущий тариф:\n"
            "{plan}\n\n"
            "Действует до:\n"
            "{expires_at}"
        ),
        
        "plan_trial": "Пробный период",
        "btn_pay_plan": "💳 Оплатить",

        "invalid_mute_duration": "❌ Неверный срок ограничения.",
        "user_not_found": "❌ Не удалось найти пользователя.",
        "user_muted": "🔒 {name} получил ограничение.\n\nСрок: {duration}",

        "user_kicked": "👢 {name} удалён из группы.",
        "user_banned": "⛔️ {name} заблокирован в группе.",
        "user_unmuted": "🔓 {name} снова может писать.",
        "user_unbanned": "✅ {name} разблокирован.",

        "limit_reached_ban": (
            "⛔️ {name} заблокирован в группе.\n\n"
            "Причина: {reason}"
        ),

        "guide_choose_section": "📘 Выберите раздел:",
        "btn_guide_bad_words": "📘 Маты",
        "btn_guide_ads": "📘 Рекламы",
        "btn_guide_warnings": "📘 Предупреждения",
        "btn_guide_restrictions": "📘 Ограничения",
        "btn_guide_settings": "📘 Настройки",
        "btn_guide_required_subs": "📘 Обязательные подписки",
        "btn_guide_transfer": "📘 Перенос настроек",
        "btn_guide_plan": "📘 План группы",
        
        "guide_bad_words_text": (
            "<b>Маты</b> — это фильтр, который определяет запрещённые слова "
            "в сообщениях пользователей, даже если они находятся внутри большого текста.\n\n"
            "Добавить слова можно в этом разделе с помощью кнопки «Добавить».\n\n"
            "Вы можете добавить сразу несколько слов одновременно, "
            "разделяя их пробелом. Использовать запятые или другие "
            "разделители не нужно.\n\n"
            "Также поддерживаются слова содержащие символы и знаки, например:\n"
            "<blockquote>• сло’во\n"
            "• сл@во\n"
            "• сл*во</blockquote>\n\n"
            "Для проверки наличия слова в словаре используйте кнопку «Поиск». "
            "Поиск принимает как сами слова, так и их номер в списке.\n\n"
            "Чтобы удалить слово, сначала найдите его через «Поиск», "
            "а затем нажмите кнопку «Удалить» в открывшемся окне."
        ),
        "guide_ads_text": (
            "<b>Рекламы</b> — это фильтр, который определяет рекламу, "
            "ссылки и рекламные тексты в сообщениях пользователей.\n\n"
            "Этот раздел состоит из нескольких отдельных фильтров.\n\n"
            "<b>Блокировка ссылок</b>\n"
            "Этот фильтр определяет некоторые сайты, домены и ссылки. "
            "Если данный переключатель включён, бот автоматически "
            "проверяет ссылки и применяет действия согласно правилам.\n\n"
            "Если вы не хотите, чтобы некоторые ссылки в группе "
            "определялись автоматически, рекомендуем отключить "
            "этот переключатель и использовать раздел "
            "<b>Другие ссылки</b>.\n\n"
            "<b>Другие ссылки</b>\n"
            "Сюда вы можете добавлять любые ссылки по своему желанию. "
            "Отправленный текст принимается как единое значение.\n\n"
            "Фильтр работает только если рекламная ссылка "
            "полностью найдена внутри текста "
            "(примеры указаны ниже).\n\n"
            "<b>Рекламные фразы</b>\n"
            "Бот также умеет определять рекламные тексты. "
            "Отправленный текст принимается как единое значение.\n\n"
            "Фильтр работает только если фраза полностью "
            "найдена внутри текста.\n\n"
            "<blockquote>Например, если добавлена фраза "
            "<b><i>накручу ботов</i></b>:\n\n"
            "• Я <b><i>накручу ботов</i></b>, пишите\n"
            "→ фильтр сработает\n\n"
            "• Я <b><i>накручу</i></b> вам <b><i>ботов</i></b>, пишите\n"
            "→ фильтр не сработает\n\n"
            "Потому что фраза не была найдена "
            "в тексте как единое значение.</blockquote>\n\n"
            "<b>Исключения</b>\n"
            "Исключения — это слова, тексты или ссылки, "
            "на которые не действуют фильтры и ограничения.\n\n"
            "Отправленный текст принимается как единое значение.\n\n"
            "<blockquote>Например, вы можете добавить официальную ссылку "
            "вашей группы в исключения, и на неё "
            "не будут действовать фильтры.</blockquote>\n\n"
            "Во всех разделах доступны кнопки "
            "<b>Добавить</b> и <b>Удалить</b>.\n\n"
            "Удаление работает только по номеру из списка."
        ),
        "guide_warnings_text": (
            "<b>Предупреждения</b> — это система, которая автоматически "
            "выдаёт предупреждения пользователю при нарушении правил.\n\n"
            "Предупреждения для рекламы и матов работают отдельно "
            "и имеют собственный счётчик.\n\n"
            "<blockquote>Например:\n"
            "• 2 предупреждения за рекламу\n"
            "• 1 предупреждение за мат</blockquote>\n\n"
            "В этом случае бот не объединяет их между собой.\n\n"
            "<b>Включение предупреждений</b>\n"
            "Если данный переключатель включён, бот отправляет сообщение "
            "о нарушении и показывает текущее количество предупреждений пользователя.\n\n"
            "Если переключатель выключен, бот не отправляет сообщение "
            "с предупреждением, однако предупреждения всё равно продолжают учитываться.\n\n"
            "<b>Лимит предупреждений</b>\n"
            "В этом разделе вы можете указать, после какого количества "
            "нарушений пользователь получит ограничение.\n\n"
            "Однако выдавать ограничение или нет решает раздел <b>Ограничения</b>.\n\n"
            "<blockquote>Например:\n"
            "• если лимит установлен на 3\n"
            "• пользователь нарушил правило 3 раза\n"
            "→ бот автоматически применит ограничение</blockquote>\n\n"
            "После ограничения предупреждения пользователя автоматически "
            "сбрасываются до нуля.\n\n"
            "Лимиты для рекламы и матов работают отдельно друг от друга."
        ),
        "guide_restrictions_text": (
            "<b>Ограничения</b> — это система, которая определяет, "
            "какое наказание получит пользователь после достижения "
            "лимита предупреждений.\n\n"

            "Ограничения для рекламы и матов работают отдельно "
            "и имеют собственные независимые настройки.\n\n"

            "<blockquote>Например:\n"
            "• ban за рекламу\n"
            "• mute на 1 день за мат</blockquote>\n\n"

            "В этом случае бот не объединяет их между собой.\n\n"

            "<b>Включение ограничений</b>\n"
            "Если данный переключатель включён, бот автоматически "
            "применяет наказание после достижения лимита предупреждений.\n\n"

            "Если переключатель выключен, предупреждения продолжают "
            "учитываться, однако ограничения выдаваться не будут.\n\n"

            "<b>Срок ограничения</b>\n"
            "В этом разделе вы можете указать, на какой срок "
            "пользователь будет ограничен.\n\n"

            "Бот поддерживает следующие форматы:\n\n"

            "• s — секунды\n"
            "• m — минуты\n"
            "• h — часы\n"
            "• d — дни\n"
            "• w — недели\n"
            "• mo — месяцы\n\n"

            "Также поддерживаются:\n"
            "• forever — вечный mute\n"
            "• ban — исключение и блокировка пользователя\n\n"

            "<blockquote>Например:\n"
            "• <b>1d</b> — ограничение на 1 день\n"
            "• <b>2h 30m</b> — ограничение на 2 часа 30 минут\n"
            "• <b>forever</b> — вечное ограничение\n"
            "• <b>ban</b> — пользователь будет исключён и заблокирован\n\n"

            "Максимальный срок ограничения — <b>12 месяцев.</b>\n"
            "Минимальный срок ограничения — <b>1 минута.</b>\n\n"

            "❗️Форматы с повторяющимися значениями, например:\n"
            "• 1m 1m\n"
            "• 2h 2h 30m\n"
            "не поддерживаются.</blockquote>\n\n"

            "Если пользователь получает ограничение, бот автоматически "
            "отправляет сообщение в группу и указывает причину ограничения.\n\n"

            "Отправка сообщения зависит от того, включён ли раздел "
            "<b>Предупреждения</b>."
        ),
        "guide_settings_text": (
            "<b>Настройки</b> — это раздел для быстрого управления "
            "основными фильтрами и функциями бота.\n\n"

            "Переключатели в этом разделе используются для "
            "включения или отключения фильтров.\n\n"

            "Каждая настройка независимо влияет на системы "
            "рекламы и матов.\n\n"

            "<b>Удаление матов</b>\n"
            "Если данный переключатель включён, бот автоматически "
            "удаляет сообщения с обнаруженными матами.\n\n"

            "Если переключатель выключен:\n"
            "• сообщение не удаляется\n"
            "• однако предупреждения и ограничения продолжают работать\n\n"

            "<b>Удаление рекламы</b>\n"
            "Если данный переключатель включён, бот автоматически "
            "удаляет рекламные сообщения и ссылки.\n\n"

            "Если переключатель выключен:\n"
            "• сообщение не удаляется\n"
            "• однако предупреждения и ограничения продолжают работать\n\n"

            "<b>Удаление @username</b>\n"
            "Этот фильтр определяет текст в формате @username "
            "и автоматически удаляет его.\n\n"

            "<blockquote>Например:\n"
            "• @username\n"
            "• Привет @username, как ты</blockquote>\n\n"

            "Однако:\n"
            "• t.me/\n"
            "• https://t.me/\n\n"

            "не относятся к этому фильтру.\n\n"

            "Если переключатель выключен, бот не реагирует "
            "на сообщения с @username."
        ),
        "guide_required_subs_text": (
            "<b>Обязательные подписки</b> — это система, которая "
            "требует от пользователей подписаться на определённые "
            "каналы или группы перед отправкой сообщений в группе.\n\n"
        
            "Бот отправляет пользователю специальные кнопки "
            "для подписки и окно проверки.\n\n"
        
            "<b>Включение обязательных подписок</b>\n"
            "Если данный переключатель включён, бот автоматически "
            "проверяет подписку всех новых пользователей.\n\n"
        
            "Если переключатель выключен, система подписок не работает.\n\n"
        
            "Для работы обязательных подписок в списке должен "
            "находиться хотя бы один канал или группа.\n\n"
        
            "<b>Добавление подписки</b>\n"
            "В этом разделе вы можете добавить канал или группу "
            "для обязательной подписки.\n\n"
        
            "Для обязательной подписки поддерживаются только "
            "публичные каналы и группы. Приватные каналы "
            "и группы не принимаются.\n\n"
        
            "Отправьте ссылку на канал или группу в виде:\n\n"
        
            "• @username\n"
            "• https://t.me/\n\n"
        
            "<blockquote>"
            "❗️Принимаются только существующие каналы или группы, "
            "в которых бот является администратором.\n\n"
        
            "Перед добавлением обязательной подписки сначала "
            "добавьте данного бота в нужный канал или группу "
            "и выдайте ему права администратора.\n\n"
        
            "В противном случае бот не сможет проверять подписки, "
            "и новые пользователи могут “застрять” в ограничении."
            "</blockquote>\n\n"
        
            "<b>Список подписок</b>\n"
            "Все добавленные каналы и группы сохраняются "
            "в виде списка.\n\n"
        
            "Если канал или группа:\n"
            "• будет удалён\n"
            "• изменит username\n"
            "• удалит бота\n\n"
        
            "бот автоматически удалит его из списка.\n\n"
        
            "Если список станет пустым, обязательные подписки "
            "автоматически отключатся."
        ),
        "guide_transfer_text": (
            "<b>Перенос настроек</b> — это система быстрого "
            "копирования фильтров и настроек из одной группы в другую.\n\n"
        
            "Данный раздел предназначен для администраторов, "
            "управляющих несколькими группами.\n\n"
        
            "Перенос работает только между группами, "
            "где вы являетесь администратором "
            "и в которых присутствует данный бот.\n\n"
        
            "<b>Выборочный перенос</b>\n"
            "Вы можете самостоятельно выбрать, "
            "какие данные нужно перенести.\n\n"
        
            "<blockquote>Например:\n"
            "• словарь матов — все слова из словаря\n"
            "• настройки рекламы — список ссылок, фраз и исключений\n"
            "• предупреждения и лимиты — состояние переключателей предупреждений и количество лимитов\n"
            "• ограничения и сроки — состояние переключателей ограничений и текущие сроки\n"
            "• настройки удаления — состояние переключателей удаления фильтруемых сообщений</blockquote>\n\n"
        
            "<b>Перенос всех настроек</b>\n"
            "Данная кнопка переносит сразу все "
            "перечисленные выше фильтры и настройки.\n\n"
        
            "<b>Дополнительная информация</b>\n"
            "При переносе словаря матов и рекламных списков "
            "бот не добавляет одинаковые данные повторно.\n\n"
        
            "Если информация уже существует в другой группе, "
            "она будет пропущена, а добавлены будут "
            "только новые и отличающиеся данные.\n\n"
        
            "<b>Что не переносится</b>\n"
            "В целях безопасности список обязательных "
            "подписок не переносится.\n\n"
        
            "Перед переносом бот показывает окно "
            "итогового подтверждения и позволяет "
            "проверить выбранные данные."
        ),
    },
    "uz": {
        "start": (
            "TizimX ga xush kelibsiz.\n\n"
            "TizimX — Telegram guruhlarini avtomatik boshqarish va moderatsiya qilish tizimi.\n\n"
            "Bot quyidagilarni avtomatik nazorat qiladi:\n"
            "<b>• so‘kinish va haqoratlar</b>\n"
            "<b>• reklama va havolalar</b>\n"
            "<b>• ogohlantirish va cheklovlar</b>\n"
            "<b>• majburiy obunalar</b>\n"
            "<b>• qo‘lda moderatsiya qilish</b>\n"
            "<b>• va yana k‘op narsalar</b>\n\n"
            "Botdan to‘liq foydalanish uchun uni guruhga qo‘shib administrator huquqlarini bering.\n\n"
            "Batafsil ma’lumot va qo‘llanmalar «📘 Qo‘llanma» bo‘limida mavjud."
        ),
        "choose_language": "🌐 Tilni tanlang:",
        "language_saved": "✅ Til saqlandi: O‘zbekcha",
        "group_connected": (
            "✅ TizimX guruhga ulandi."
        ),
        "no_admin_rights": (
            "Moderatsiya ishlashi uchun botga administrator huquqini bering."
        ),
        "group_language_ru": "✅ Guruh tili rus tiliga o‘zgartirildi.",
        "group_language_uz": "✅ Guruh tili o‘zbekchaga o‘zgartirildi.",
        "private_welcome": "🛡 TizimX ga xush kelibsiz",
        "manage_button": "⚙️ Boshqarish",
        "language_button": "🌐 Til",
        "guide_button": "📘 Qo‘llanma",
        "back_button": "⬅️ Orqaga",
        "choose_group": "📂 Guruhni tanlang:",
        "no_groups": "❌ Sizda hali ulangan guruhlar yo‘q.",
        "group_panel": (
            "⚙️ Guruh sozlamalari:\n\n"
            "{title}\n\n"
            "Guruhning ID si:\n"
            "<code>{chat_id}</code>"
        ),
        "access_denied": "❌ Sizda bu guruhga kirish huquqi yo‘q.",
        "enabled": "🟢",
        "disabled": "🔴",

        "required_sub_join_text": (
            "🔒 {name}, guruhga yozish uchun "
            "quyidagilarga obuna bo‘ling:"
        ),
        "required_sub_check_button": "✅ Tekshirish",
        "required_sub_not_all": "❌ Siz barcha kanal va guruhlarga obuna bo‘lmadingiz",
        "required_sub_success": "✅ Obuna tasdiqlandi",

        "btn_bad_words": "🤬 Haqoratlar",
        "btn_ads": "🚫 Reklamalar",
        "btn_warnings": "⚠️ Ogohlantirishlar",
        "btn_restrictions": "🔒 Cheklovlar",
        "btn_settings": "⚙️ Sozlamalar",
        "btn_transfer_settings": "🔁 Sozlamalarni ko‘chirish",

        "bad_words_title": "🤬 Haqoratlar\n\n{words}\n\nSahifa {page}/{total_pages}",
        "bad_words_empty": "🤬 Haqoratlar ro‘yxati bo‘sh.",
        "btn_prev": "⬅️ Oldingi",
        "btn_next": "Keyingi ➡️",
        "btn_search": "🔍 Qidirish",
        "btn_back_panel": "⬅️ Menyuga",

        "btn_add_bad_word": "➕ Haqorat qo‘shish",
        "add_bad_word_prompt": "✍️ Yangi haqoratni kiriting.\n\nBir nechta so‘z yuborishingiz mumkin, masalan:\nso‘z1 so‘z2 so‘z3",
        "bad_words_added": "✅ Haqorat guruhga qo‘shildi.",

        "ads_panel": "🚫 Reklamalar\n\nHavolalarni bloklash: {status}",
        "links_enabled": "🟢 Yoqilgan",
        "links_disabled": "🔴 O‘chirilgan",
        "btn_disable_links": "🔴 Havolalarni bloklashni o‘chirish",
        "btn_enable_links": "🟢 Havolalarni bloklashni yoqish",
        "btn_other_links": "🔗 Boshqa havolalar",
        "btn_ad_phrases": "💬 Reklama iboralari",
        "btn_ad_exceptions": "✅ Istisnolar",
        
        "ad_links_title": "🔗 Boshqa havolalar\n\n{links}\n\nSahifa {page}/{total_pages}",
        "ad_links_empty": "🔗 Havolalar ro‘yxati bo‘sh.",
        "btn_add_ad_link": "➕ Havola qo‘shish",
        "add_ad_link_prompt": "✍️ Havolani kiriting.",
        "ad_links_added": "✅ Havola guruhga qo‘shildi.",

        "bad_word_search_prompt": "🔍 Ro'yxatdagi raqam yoki haqoratni kiriting, masalan:\n38 yoki so‘z2",
        "bad_word_not_found": "❌ Bunday haqorat mavjud emas, uni qo‘shishingiz mumkin.",
        "bad_word_found": "✅ Topildi:\n\n{index}. {word}",
        "btn_delete": "🗑 O‘chirish",
        "bad_word_deleted": "✅ Haqorat o‘chirildi.",

        "ad_phrases_title": "💬 Reklama iboralari\n\n{phrases}\n\nSahifa {page}/{total_pages}",
        "ad_phrases_empty": "💬 Reklama iboralari ro‘yxati bo‘sh.",
        "btn_add_ad_phrase": "➕ Ibora qo‘shish",
        "add_ad_phrase_prompt": "✍️ Reklama iborasini kiriting.",
        "ad_phrase_added": "✅ Reklama iborasi qo‘shildi.",

        "btn_delete_ad_link": "🗑 Havolani o‘chirish",
        "delete_ad_link_prompt": "🗑 O‘chirish uchun havola raqamini kiriting.",
        "ad_link_deleted": "✅ Havola o‘chirildi.",
        "ad_link_not_found": "❌ Bunday havola yo‘q.",
        
        "btn_delete_ad_phrase": "🗑 Iborani o‘chirish",
        "delete_ad_phrase_prompt": "🗑 O‘chirish uchun ibora raqamini kiriting.",
        "ad_phrase_deleted": "✅ Ibora o‘chirildi.",
        "ad_phrase_not_found": "❌ Bunday ibora yo‘q.",

        "ad_exceptions_title": "✅ Istisnolar\n\n{exceptions}\n\nSahifa {page}/{total_pages}",
        "ad_exceptions_empty": "✅ Istisnolar ro‘yxati bo‘sh.",
        "btn_add_ad_exception": "➕ Istisno qo‘shish",
        "btn_delete_ad_exception": "🗑 Istisnoni o‘chirish",
        "add_ad_exception_prompt": "✍️ Istisnoni kiriting.",
        "ad_exception_added": "✅ Istisno qo‘shildi.",
        "delete_ad_exception_prompt": "🗑 O‘chirish uchun istisno raqamini kiriting.",
        "ad_exception_deleted": "✅ Istisno o‘chirildi.",
        "ad_exception_not_found": "❌ Bunday istisno yo‘q.",

        "warnings_panel": (
            "⚠️ Ogohlantirishlar\n\n"
            "Haqorat uchun ogohlantirish:\n{bad_words_status}\n\n"
            "Reklama uchun ogohlantirish:\n{ads_status}"
        ),
        
        "warn_enabled": "🟢 YOQILGAN",
        "warn_disabled": "🔴 O‘CHIRILGAN",
        
        "btn_warn_bad_words_on": "🟢 Haqorat uchun ogohlantirishni yoqish",
        "btn_warn_bad_words_off": "🔴 Haqorat uchun ogohlantirishni o‘chirish",
        
        "btn_warn_ads_on": "🟢 Reklama uchun ogohlantirishni yoqish",
        "btn_warn_ads_off": "🔴 Reklama uchun ogohlantirishni o‘chirish",
        
        "btn_bad_words_warn_limit": "🤬 Haqoratni ogohlantirish soni: {limit}",
        "btn_ads_warn_limit": "🚫 Reklamani ogohlantirish soni: {limit}",
        "choose_warn_limit": "⚠️ Ogohlantirishlar sonini tanlang:",
        "warn_limit_saved": "✅ Ogohlantirishlar soni saqlandi.",

        "warning_message": (
            "⚠️ {name}, guruh qoidasi buzildi.\n\n"
            "Sabab: {reason}\n"
            "Ogohlantirish: {count}/{limit}"
        ),
        "reason_bad_word": "taqiqlangan so'z",
        "reason_ads": "reklama",
        "limit_reached": (
            "🔒 {name} cheklov oldi.\n\n"
            "Muddat: {duration}\n"
            "Sabab: {reason}"
        ),
        "restrictions_panel": (
            "🔒 Cheklovlar\n\n"
            "Haqorat uchun cheklov:\n{bad_words_status}\n"
            "Reklama uchun cheklov:\n{ads_status}\n\n"
            "Haqorat uchun cheklov muddati:\n🕓 {bad_words_duration}\n"
            "Reklama uchun cheklov muddati:\n🕓 {ads_duration}"
        ),
        "btn_punish_bad_words_on": "🟢 Haqorat uchun cheklovni yoqish",
        "btn_punish_bad_words_off": "🔴 Haqorat uchun cheklovni o‘chirish",
        "btn_punish_ads_on": "🟢 Reklama uchun cheklovni yoqish",
        "btn_punish_ads_off": "🔴 Reklama uchun cheklovni o‘chirish",
        "btn_bad_words_punish_duration": "⏳ Haqorat uchun muddat",
        "btn_ads_punish_duration": "⏳ Reklama uchun muddat",

        "enter_duration_prompt": (
            "⏳ Cheklov muddatini kiriting.\n\n"
            "Misollar:\n"
            "30m = 30 daqiqa\n"
            "12h = 12 soat\n"
            "7d = 7 kun\n"
            "2d 5h = 2 kun 5 soat\n"
            "1mo = 1 oy\n"
            "Max. muddat - 12 oy\n"
            "Min. muddat - 1 daqiqa\n\n"
            "Ban = bloklash\n"
            "Forever = doimiy muddat"
        ),
        "invalid_duration_format": (
            "❌ Bunday format qo‘llab-quvvatlanmaydi.\n\n"
            "Misollar:\n"
            "30m = 30 daqiqa\n"
            "12h = 12 soat\n"
            "7d = 7 kun\n"
            "2d 5h = 2 kun 5 soat\n"
            "1mo = 1 oy\n"
            "Max. muddat - 12 oy\n"
            "Min. muddat - 1 daqiqa\n\n"
            "Ban = bloklash\n"
            "Forever = doimiy muddat"
        ),
        "duration_saved": "✅ Cheklov muddati saqlandi.",
        "btn_open_section": "↩️ Bo‘limni ochish",

        "settings_panel": (
            "⚙️ Sozlamalar\n\n"
            "Haqoratlarni o‘chirish:\n{bad_words_status}\n\n"
            "Reklamalarni o‘chirish:\n{ads_status}\n\n"
            "@username o‘chirish:\n{usernames_status}"
        ),
        
        "btn_toggle_bad_words_on": "🟢 Haqoratlarni tozalashni yoqish",
        "btn_toggle_bad_words_off": "🔴 Haqoratlarni tozalashni o‘chirish",
        
        "btn_toggle_ads_on": "🟢 Reklamalarni tozalashni yoqish",
        "btn_toggle_ads_off": "🔴 Reklamalarni tozalashni o‘chirish",
        
        "btn_toggle_usernames_on": "🟢 @username tozalashni yoqish",
        "btn_toggle_usernames_off": "🔴 @username tozalashni o‘chirish",

        "btn_required_subs": "📌 Majburiy obunalar",
        "required_subs_panel": (
            "📌 Majburiy obunalar\n\n"
            "Holat: {status}\n\n"
            "Ro‘yxat:\n{subs}"
        ),
        "required_subs_empty": "Hozircha bo‘sh.",
        "btn_required_subs_on": "🟢 Majburiy obunalarni yoqish",
        "btn_required_subs_off": "🔴 Majburiy obunalarni o‘chirish",
        "btn_add_required_sub": "➕ Obuna qo‘shish",
        "btn_delete_required_sub": "🗑 Obunani o‘chirish",

        "add_required_sub_prompt": (
            "➕ Majburiy obuna uchun kanal yoki guruhni yuboring.\n\n"
            "Yuborishingiz mumkin:\n"
            "• @username\n"
            "• https://t.me/"
        ),
        "required_sub_added": "✅ Obuna qo‘shildi.",
        "delete_required_sub_prompt": "🗑 O‘chirish uchun obuna raqamini kiriting.",
        "required_sub_deleted": "✅ Obuna o‘chirildi.",
        "required_sub_not_found": "❌ Bunday obuna yo‘q.",

        "required_sub_invalid": (
            "❌ Kanal yoki guruh noto‘g‘ri.\n\n"
            "Quyidagi formatda yuboring:\n"
            "• @username\n"
            "yoki\n"
            "• https://t.me/"
        ),
        "required_sub_not_accessible": (
            "❌ Bu kanal yoki guruh topilmadi.\n\n"
            "Username ni tekshiring yoki botni u yerga admin qiling."
        ),
        "required_subs_empty_alert": "❌ Majburiy obunani yoqish uchun avval kamida bitta obuna qo‘shing.",

        "transfer_panel": (
            "🔁 Sozlamalarni ko‘chirish\n\n"
            "Ko‘chirmoqchi bo‘lgan sozlamalar va ma’lumotlarni tanlang."
        ),
        "btn_transfer_bad_words": "So‘kinishlar lug‘ati: {status}",
        "btn_transfer_ads": "Reklamalar ro‘yxati: {status}",
        "btn_transfer_warnings": "Ogohlantirishlar va limitlar: {status}",
        "btn_transfer_restrictions": "Cheklovlar va muddatlar: {status}",
        "btn_transfer_delete_settings": "O‘chirish sozlamalari: {status}",
        "btn_transfer_all": "🌟 Barcha sozlamalar",
        "btn_transfer_selected": "🚀 Tanlanganlarni ko‘chirish",
        "transfer_nothing_selected": "❌ Ko‘chirish uchun kamida bitta bandni tanlang.",
        "transfer_choose_group": "📂 Sozlamalar ko‘chiriladigan guruhni tanlang:",
        "transfer_no_target_groups": "❌ Ko‘chirish uchun boshqa mavjud guruh yo‘q.",

        "transfer_confirm_text": (
            "⚠️ Sozlamalarni ko‘chirishni tasdiqlang\n\n"
            "Qaysi guruhdan:\n{source_title}\n\n"
            "Qaysi guruhga:\n{target_title}\n\n"
            "Ko‘chiriladi:\n{items}"
        ),
        "btn_confirm": "✅ Tasdiqlash",
        
        "transfer_item_bad_words": "• So‘kinishlar lug‘ati",
        "transfer_item_ads": "• Reklamalar ro‘yxati",
        "transfer_item_warnings": "• Ogohlantirishlar va limitlar",
        "transfer_item_restrictions": "• Cheklovlar va muddatlar",
        "transfer_item_delete_settings": "• O‘chirish sozlamalari",
        "transfer_done": "✅ Sozlamalar muvaffaqiyatli ko‘chirildi.",

        "btn_group_plan": "💎 Guruh tarif rejasi",
        "group_plan_text": (
            "💎 Guruh tarif rejasi\n\n"
            "Joriy tarif:\n"
            "{plan}\n\n"
            "Amal qilish muddati:\n"
            "{expires_at}"
        ),
        
        "plan_trial": "Sinov muddati",
        "btn_pay_plan": "💳 To‘lash",

        "invalid_mute_duration": "❌ Cheklov muddati noto‘g‘ri.",
        "user_not_found": "❌ Foydalanuvchini topib bo‘lmadi.",
        "user_muted": "🔒 {name} cheklandi.\n\nMuddat: {duration}",

        "user_kicked": "👢 {name} guruhdan chiqarildi.",
        "user_banned": "⛔️ {name} guruhda bloklandi.",
        "user_unmuted": "🔓 {name} yana yozishi mumkin.",
        "user_unbanned": "✅ {name} blokdan chiqarildi.",

        "limit_reached_ban": (
            "⛔️ {name} guruhda bloklandi.\n\n"
            "Sabab: {reason}"
        ),

        "guide_choose_section": "📘 Bo‘limni tanlang:",
        "btn_guide_bad_words": "📘 So‘kinishlar",
        "btn_guide_ads": "📘 Reklamalar",
        "btn_guide_warnings": "📘 Ogohlantirishlar",
        "btn_guide_restrictions": "📘 Cheklovlar",
        "btn_guide_settings": "📘 Sozlamalar",
        "btn_guide_required_subs": "📘 Majburiy obunalar",
        "btn_guide_transfer": "📘 Sozlamalarni ko‘chirish",
        "btn_guide_plan": "📘 Guruh tarif rejasi",
        
        "guide_bad_words_text": (
            "<b>Haqoratlar</b> — foydalanuvchi yuborgan xabardagi "
            "taqiqlangan so‘zlarni aniqlovchi filtr hisoblanadi, "
            "hatto ular katta matn ichida bo‘lsa ham.\n\n"
            "So‘zlarni ushbu bo‘limdagi «Qo‘shish» tugmasi orqali qo‘shishingiz mumkin.\n\n"
            "Bir vaqtning o‘zida bir nechta so‘zni qo‘shish mumkin. "
            "Buning uchun so‘zlar orasini oddiy probel bilan ajrating. "
            "Vergul yoki boshqa belgilar kerak emas.\n\n"
            "Shuningdek, belgilar bilan yozilgan so‘zlar ham qabul qilinadi, masalan:\n"
            "<blockquote>• ha'qorat\n"
            "• h@qorat\n"
            "• h*qorat</blockquote>\n\n"
            "So‘z lug‘atda mavjudligini tekshirish uchun «Qidirish» tugmasidan foydalaning. "
            "Qidiruv so‘zning o‘zi yoki uning ro‘yxatdagi raqami orqali ishlaydi.\n\n"
            "So‘zni o‘chirish uchun avval uni «Qidirish» orqali toping, "
            "so‘ng ochilgan oynada «O‘chirish» tugmasini bosing."
        ),
        "guide_ads_text": (
            "<b>Reklamalar</b> — foydalanuvchilar yuborgan reklama, "
            "havola va reklama mazmunidagi matnlarni aniqlovchi filtr.\n\n"
            "Ushbu bo‘lim bir nechta alohida filtrlardan iborat.\n\n"
            "<b>Havolalarni bloklash</b>\n"
            "Bu filtr ayrim saytlar, domenlar va havolalarni aniqlaydi. "
            "Agar ushbu tugma yoqilgan bo‘lsa, bot havolalarni avtomatik "
            "tekshiradi va qoidaga qarab choralar ko‘radi.\n\n"
            "Agar guruhingizda ayrim havolalar ruxsatsiz aniqlanishini "
            "istamasangiz, ushbu tugmani o‘chirib qo‘yib, "
            "<b>Boshqa havolalar</b> bo‘limidan foydalanishni tavsiya qilamiz.\n\n"
            "<b>Boshqa havolalar</b>\n"
            "Bu yerga o‘zingiz istagan havolalarni qo‘shishingiz mumkin. "
            "Yuborgan matningiz bir butun ma’lumot sifatida qabul qilinadi.\n\n"
            "Filtr faqat reklama havolasi matn ichida to‘liq ko‘rinishda "
            "topilganda ishlaydi (misollar pastda keltirilgan).\n\n"
            "<b>Reklama iboralari</b>\n"
            "Bot reklama mazmunidagi matnlarni ham aniqlay oladi. "
            "Yuborgan matningiz bir butun ma’lumot sifatida qabul qilinadi.\n\n"
            "Filtr faqat ibora matn ichida to‘liq ko‘rinishda topilganda ishlaydi.\n\n"
            "<blockquote>Masalan, agar <b><i>odam yig‘aman</i></b> iborasi qo‘shilgan bo‘lsa:\n\n"
            "• Men <b><i>odam yig‘aman</i></b>, yozinglar\n"
            "→ filtr ishlaydi\n\n"
            "• Men <b><i>odam</i></b> sizlarga <b><i>yig‘aman</i></b>, yozinglar\n"
            "→ filtr ishlamaydi\n\n"
            "Chunki ibora matn ichida bir butun holatda topilmadi.</blockquote>\n\n"
            "<b>Istisnolar</b>\n"
            "Istisnolar — bu hech qanday filtr va cheklov ishlamaydigan "
            "so‘z, matn yoki havolalar.\n\n"
            "Yuborgan matningiz bir butun ma’lumot sifatida qabul qilinadi.\n\n"
            "<blockquote>Masalan, guruhingizning rasmiy havolasini istisnoga "
            "qo‘shsangiz, unga hech qanday filtr ta’sir qilmaydi.</blockquote>\n\n"
            "Barcha bo‘limlarda <b>Qo‘shish</b> va <b>O‘chirish</b> "
            "tugmalari mavjud.\n\n"
            "O‘chirish faqat ro‘yxatdagi raqam orqali ishlaydi."
        ),
        "guide_warnings_text": (
            "<b>Ogohlantirishlar</b> — foydalanuvchi qoidalarni buzganida "
            "unga avtomatik ogohlantirish beruvchi tizim.\n\n"

            "Ogohlantirishlar reklama va so‘kinish filtrlari uchun alohida "
            "ishlaydi va har biri o‘zining alohida hisobiga ega.\n\n"

            "<blockquote>Masalan:\n"
            "• reklama uchun 2 ta ogohlantirish\n"
            "• haqorat uchun 1 ta ogohlantirish</blockquote>\n\n"

            "Bot bu holatda ularni birlashtirmaydi.\n\n"

            "<b>Ogohlantirishlarni yoqish</b>\n"
            "Agar ushbu tugma yoqilgan bo‘lsa, bot foydalanuvchiga "
            "qoidabuzarlik haqida xabar yuboradi va ogohlantirish sonini ko‘rsatadi.\n\n"

            "Agar tugma o‘chirilgan bo‘lsa, bot ogohlantirish xabarini yubormaydi, "
            "ammo ogohlantirishlar baribir hisoblanadi.\n\n"

            "<b>Ogohlantirish limiti</b>\n"
            "Bu bo‘limda foydalanuvchi necha marta qoida buzganidan keyin "
            "cheklov olishini belgilashingiz mumkin.\n\n"

            "Ammo cheklov berish yoki bermaslikni <b>Cheklovlar</b> bo‘limi hal qiladi.\n\n"

            "<blockquote>Masalan:\n"
            "• limit 3 bo‘lsa\n"
            "• foydalanuvchi 3 marta qoida buzsa\n"
            "→ bot avtomatik cheklov qo‘llaydi</blockquote>\n\n"

            "Cheklovdan keyin foydalanuvchining ogohlantirishlari avtomatik "
            "ravishda nolga tushiriladi.\n\n"

            "Reklama va haqorat uchun limitlar alohida ishlaydi."
        ),
        "guide_restrictions_text": (
            "<b>Cheklovlar</b> — foydalanuvchi ogohlantirish limitiga "
            "yetganidan keyin qanday jazo olishini boshqaruvchi tizim.\n\n"

            "Cheklovlar reklama va haqorat uchun alohida ishlaydi "
            "va har biri o‘zining mustaqil sozlamalariga ega.\n\n"

            "<blockquote>Masalan:\n"
            "• reklama uchun ban\n"
            "• haqorat uchun 1 kun mute</blockquote>\n\n"

            "Bot bu holatda ularni birlashtirmaydi.\n\n"

            "<b>Cheklovlarni yoqish</b>\n"
            "Agar ushbu tugma yoqilgan bo‘lsa, foydalanuvchi "
            "ogohlantirish limitiga yetganda bot avtomatik "
            "jazo qo‘llaydi.\n\n"

            "Agar tugma o‘chirilgan bo‘lsa, ogohlantirishlar "
            "hisoblanishda davom etadi, ammo hech qanday "
            "cheklov berilmaydi.\n\n"

            "<b>Cheklov muddati</b>\n"
            "Bu bo‘limda foydalanuvchi qancha muddatga "
            "cheklanishini belgilashingiz mumkin.\n\n"

            "Bot quyidagi formatlarni qo‘llab-quvvatlaydi:\n\n"

            "• s — soniya\n"
            "• m — daqiqa\n"
            "• h — soat\n"
            "• d — kun\n"
            "• w — hafta\n"
            "• mo — oy\n\n"

            "Shuningdek:\n"
            "• forever — doimiy mute\n"
            "• ban — haydash va bloklash\n\n"

            "<blockquote>Masalan:\n"
            "• <b>1d</b> — kiritsangiz, cheklov 1 kunga beriladi\n"
            "• <b>2h 30m</b> — kiritsangiz, cheklov 2 soatu 30 daqiqaga beriladi\n"
            "• <b>forever</b> — kiritsangiz, cheklov doimiyga beriladi\n"
            "• <b>ban</b> — kiritsangiz, foydalanuvchi guruhdan haydaladi va bloklanadi\n\n"

            "Maksimal cheklov muddati — <b>12 oy.</b>\n"
            "Minimal cheklov muddati — <b>1 daqiqa.</b>\n\n"

            "❗️<b>1m 1m</b> yoki <b>2h 2h 30m</b> kabi takrorlanuvchi "
            "formatlar qo‘llab-quvvatlanmaydi.</blockquote>\n\n"

            "Agar foydalanuvchi cheklansa, bot guruhga avtomatik "
            "xabar yuboradi va cheklov sababini ko‘rsatadi.\n\n"

            "Xabar yuborilishi <b>Ogohlantirishlar</b> bo‘limi "
            "yoqilgan yoki o‘chirilganligiga bog‘liq."
        ),
        "guide_settings_text": (
            "<b>Sozlamalar</b> — botning asosiy filtr va funksiyalarini "
            "tez boshqarish bo‘limi.\n\n"

            "Ushbu bo‘limdagi tugmalar filtrlarni yoqish yoki "
            "o‘chirish uchun ishlatiladi.\n\n"

            "Har bir sozlama reklama va so‘kinish tizimlariga "
            "mustaqil ta’sir qiladi.\n\n"

            "<b>Haqoratlarni o‘chirish</b>\n"
            "Agar ushbu tugma yoqilgan bo‘lsa, bot aniqlangan "
            "haqoratli xabarlarni avtomatik o‘chiradi.\n\n"

            "Agar tugma o‘chirilgan bo‘lsa:\n"
            "• xabar o‘chirilmaydi\n"
            "• ammo ogohlantirish va cheklovlar ishlashda davom etadi\n\n"

            "<b>Reklamalarni o‘chirish</b>\n"
            "Agar ushbu tugma yoqilgan bo‘lsa, bot reklama "
            "va havolali xabarlarni avtomatik o‘chiradi.\n\n"

            "Agar tugma o‘chirilgan bo‘lsa:\n"
            "• xabar o‘chirilmaydi\n"
            "• ammo ogohlantirish va cheklovlar ishlashda davom etadi\n\n"

            "<b>@username ni o‘chirish</b>\n"
            "Bu filtr foydalanuvchi yuborgan @username "
            "ko‘rinishidagi matnlarni aniqlaydi va avtomatik o‘chiradi.\n\n"

            "<blockquote>Masalan:\n"
            "• @username\n"
            "• Salom @username, qalaysan</blockquote>\n\n"

            "Ammo quyidagilar:\n"
            "• t.me/\n"
            "• https://t.me/\n\n"

            "ushbu filtrga kirmaydi.\n\n"

            "Agar tugma o‘chirilgan bo‘lsa, bot "
            "@username matnlariga ta’sir qilmaydi."
        ),
        "guide_required_subs_text": (
            "<b>Majburiy obunalar</b> — foydalanuvchilar guruhga "
            "yozishidan oldin ma’lum kanal yoki guruhlarga "
            "obuna bo‘lishini talab qiluvchi tizim.\n\n"
        
            "Bot foydalanuvchiga obuna bo‘lish uchun maxsus "
            "tugmalar va tekshiruv oynasini yuboradi.\n\n"
        
            "<b>Majburiy obunalarni yoqish</b>\n"
            "Agar ushbu tugma yoqilgan bo‘lsa, bot barcha yangi "
            "foydalanuvchilarning obunasini avtomatik tekshiradi.\n\n"
        
            "Agar tugma o‘chirilgan bo‘lsa, obuna tizimi ishlamaydi.\n\n"
        
            "Majburiy obunalar ishlashi uchun ro‘yxatda kamida "
            "bitta kanal yoki guruh bo‘lishi kerak.\n\n"
        
            "<b>Obuna qo‘shish</b>\n"
            "Bu bo‘lim orqali majburiy obuna uchun kanal "
            "yoki guruh qo‘shishingiz mumkin.\n\n"
        
            "Majburiy obuna uchun faqat ommaviy kanal "
            "va guruhlar qo‘llab-quvvatlanadi. "
            "Maxfiy kanal va guruhlar qabul qilinmaydi.\n\n"
        
            "Kanal yoki guruh havolasini shu ko'rinishda yuboring:\n\n"
        
            "• @username\n"
            "• https://t.me/\n\n"
        
            "<blockquote>"
            "❗️Faqat mavjud va bot admin bo‘lgan kanal "
            "yoki guruhlar qabul qilinadi.\n\n"
        
            "Majburiy obuna uchun qo‘shayotgan kanal "
            "yoki guruhingizga avval ushbu botni qo‘shib, "
            "administrator qiling.\n\n"
        
            "Aks holda bot obunani tekshira olmaydi "
            "va yangi foydalanuvchilar cheklovda "
            "qolib ketishi mumkin."
            "</blockquote>\n\n"
        
            "<b>Obuna ro‘yxati</b>\n"
            "Barcha qo‘shilgan kanal va guruhlar "
            "ro‘yxat ko‘rinishida saqlanadi.\n\n"
        
            "Agar kanal yoki guruh:\n"
            "• o‘chirib yuborilsa\n"
            "• username o‘zgarsa\n"
            "• bot chiqarib yuborilsa\n\n"
        
            "bot uni avtomatik ravishda "
            "ro‘yxatdan olib tashlaydi.\n\n"
        
            "Agar ro‘yxat bo‘sh qolsa, majburiy "
            "obunalar avtomatik ravishda o‘chiriladi."
        ),
        "guide_transfer_text": (
            "<b>Sozlamalarni ko‘chirish</b> — bir guruhdagi "
            "filtr va sozlamalarni boshqa guruhga "
            "tez nusxalash tizimi.\n\n"
        
            "Bu bo‘lim bir nechta guruhlarni "
            "boshqaradigan administratorlar uchun mo‘ljallangan.\n\n"
        
            "Ko‘chirish faqat siz admin bo‘lgan "
            "va ushbu bot mavjud guruhlar orasida ishlaydi.\n\n"
        
            "<b>Tanlab ko‘chirish</b>\n"
            "Siz qaysi ma’lumotlarni ko‘chirishni "
            "mustaqil tanlashingiz mumkin.\n\n"
        
            "<blockquote>Masalan:\n"
            "• haqoratlar lug‘ati — lug‘atdagi barcha so‘zlar\n"
            "• reklama sozlamalari — havolalar, iboralar va istisnolar ro‘yxati\n"
            "• ogohlantirishlar va limitlar — ogohlantirish tugmalari holati va limitlar soni\n"
            "• cheklovlar va muddatlar — cheklov tugmalari holati va joriy muddatlar\n"
            "• o‘chirish sozlamalari — filtrlangan xabarlarni o‘chirish tugmalari holati</blockquote>\n\n"
        
            "<b>Barcha sozlamalarni ko‘chirish</b>\n"
            "Ushbu tugma yuqorida keltirilgan barcha "
            "filtr va sozlamalarni birdaniga ko‘chiradi.\n\n"
        
            "<b>Qo‘shimcha ma’lumot</b>\n"
            "Haqoratlar lug‘ati va reklama ro‘yxatlari "
            "ko‘chirilayotganda bot bir xil ma’lumotlarni "
            "qayta qo‘shmaydi.\n\n"
        
            "Agar ma’lumot boshqa guruhda avvaldan mavjud bo‘lsa, "
            "u o‘tkazib yuboriladi, faqat yangi va "
            "farqli ma’lumotlar qo‘shiladi.\n\n"
        
            "<b>Nimalar ko‘chirilmaydi</b>\n"
            "Xavfsizlik yuzasidan majburiy obunalar "
            "ro‘yxati ko‘chirilmaydi.\n\n"
        
            "Ko‘chirishdan oldin bot yakuniy "
            "tasdiqlash oynasini ko‘rsatadi va "
            "tanlangan ma’lumotlarni tekshirish "
            "imkonini beradi."
        ),
    }
}

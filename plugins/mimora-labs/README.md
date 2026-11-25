# Mimora Labs — плагин для Claude и ИИ-ассистентов

Плагин подключает MCP-коннектор **Mimora Labs** (`https://mcp.mimora.io/mcp`) и восемь готовых сценариев проверки маркетинговых гипотез на ИИ-панелях:

- `/mimora-labs:check-offer` — быстрая проверка одного оффера, текста или идеи на ручной панели
- `/mimora-labs:ab-copy` — выбор лучшего из 3–6 текстовых вариантов (заголовки, офферы, посты)
- `/mimora-labs:creative-tournament` — турнир из 2–15 картинок-креативов (батчами до 6 медиа в одном раунде; видео пока недоступно)
- `/mimora-labs:deep-panel` — глубокое исследование на автономной панели до 5 раундов (формат концепт: текст, оффер, идея, пост или картинка)
- `/mimora-labs:pick-audience` — бесплатный подбор аудитории и оценка размера выборки
- `/mimora-labs:rewrite-and-retest` — правка текста по возражениям и повторная проверка
- `/mimora-labs:objection-handling` — разбор возражений из уже проведённой панели
- `/mimora-labs:client-report` — короткий отчёт клиенту по итогам панели

## Установка в Claude Code

```bash
claude plugin marketplace add MaydanNay/mimora-labs-plugin
claude plugin install mimora-labs@mimora-labs
```

После установки откройте `/mcp` в сессии Claude Code, выберите `mimora_labs` и войдите в аккаунт Mimora Labs.

Проверка: введите `/` и убедитесь, что появились команды `mimora-labs:…`.

## Установка в приложении Claude (Web / Desktop)

1. Откройте **Customize → Plugins**.
2. Нажмите **Add → Add marketplace** и укажите GitHub-репозиторий `MaydanNay/mimora-labs-plugin` (или загрузите zip-архив плагина со страницы [интеграций Mimora Labs](https://labs.mimora.io/integrations)).
3. Установите плагин `mimora-labs`.
4. Во вкладке **Connectors** подключите коннектор Mimora Labs и войдите в свой аккаунт.

## Аккаунт и кредиты

- Регистрация, вход и баланс: [https://labs.mimora.io](https://labs.mimora.io)
- Подробнее об интеграциях: [https://labs.mimora.io/docs#integrations](https://labs.mimora.io/docs#integrations)
- Сначала выполняются бесплатные шаги (лимиты, подбор аудитории и смета). Платный запуск панели происходит только после вашего явного согласия («запускай»).

## Оговорка

Результаты — мнение смоделированной ИИ-панели Mimora Labs, а не исследование реальных людей. Цифры, названные ИИ-людьми, не переносятся в выводы без пометки о проверке. Перед крупным бюджетом проверяйте решения на реальной выборке.

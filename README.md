# Mimora Labs Plugin

Официальный плагин и маркетплейс-репозиторий **Mimora Labs** для Claude и других ИИ-ассистентов с поддержкой MCP и `SKILL.md`.

Подключает MCP-сервер Mimora Labs (`https://mcp.mimora.io/mcp`) и 8 готовых сценариев проверки офферов, креативов, аудиторий и рекламных гипотез на ИИ-панелях.

## Сценарии

| Команда | Для чего нужна |
| --- | --- |
| `/mimora-labs:check-offer` | Быстрая проверка одного оффера, текста или идеи (реакция + дожим скептиков) |
| `/mimora-labs:ab-copy` | Выбор лучшего из 3–6 текстовых вариантов (заголовки, офферы, посты) |
| `/mimora-labs:creative-tournament` | Турнир из 2–15 картинок-креативов (батчами до 6 медиа в одном раунде; видео пока недоступно) |
| `/mimora-labs:deep-panel` | Глубокое исследование на автономной панели до 5 раундов (формат концепт: текст, оффер, идея, пост или картинка) |
| `/mimora-labs:pick-audience` | Бесплатный подбор сегментов аудитории и оценка выборки |
| `/mimora-labs:rewrite-and-retest` | Переписывание текста по возражениям и повторный тест |
| `/mimora-labs:objection-handling` | Структурный разбор возражений из готовой панели |
| `/mimora-labs:client-report` | Итоговый отчёт клиенту по результатам панели |

## Быстрая установка

### Claude Code

```bash
claude plugin marketplace add MaydanNay/mimora-labs-plugin
claude plugin install mimora-labs@mimora-labs
```

Затем в сессии откройте `/mcp`, выберите `mimora_labs` и авторизуйтесь в аккаунте Mimora Labs.

### Claude Web / Desktop

1. Перейдите в **Customize → Plugins → Add → Add marketplace**.
2. Укажите этот GitHub-репозиторий: `MaydanNay/mimora-labs-plugin`.
3. Установите плагин `mimora-labs` и подключите коннектор во вкладке **Connectors**.

### Другие ИИ-ассистенты (MCP + SKILL.md)

- **MCP-сервер (Streamable HTTP):** `https://mcp.mimora.io/mcp`
- **Скиллы (`SKILL.md`):** лежат в `plugins/mimora-labs/skills/*/SKILL.md` — их можно подключить в любой агент, поддерживающий стандарт Agent Skills.

## Полезные ссылки

- Личный кабинет и кредиты: [https://labs.mimora.io](https://labs.mimora.io)
- Документация по интеграциям: [https://labs.mimora.io/docs#integrations](https://labs.mimora.io/docs#integrations)

## Безопасность и оговорка

- Все платные запуски панелей выполняются только после явного подтверждения пользователя и предварительной сметы.
- Результаты отражают мнение смоделированной ИИ-панели Mimora Labs и не заменяют исследование реальных людей перед крупными бюджетами.

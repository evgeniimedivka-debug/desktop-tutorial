# Telegram-бот для мозгового штурма (Milis Cosmo / Milis Decor / art.Angel)

Реализация по ТЗ: бот-участник рабочей группы (Евгений + Анна), отвечает
только на упоминание `@OzonAnnabot` или reply на своё сообщение.
Стек: Telegram Bot API → webhook → Pipedream (HTTP-триггер) → Node.js →
Anthropic Messages API → Telegram `sendMessage`.

Код шага: [`component.js`](./component.js).

## Деплой в Pipedream

1. Создать Pipedream workflow с HTTP-триггером, скопировать его URL.
2. Вставить содержимое `component.js` в Node.js code step workflow.
3. Задать переменные окружения в Pipedream (Settings → Environment Variables
   или прямо в step, но НЕ хардкодить в коде):
   - `TELEGRAM_BOT_TOKEN` — токен `@OzonAnnabot`
   - `ANTHROPIC_API_KEY` — ключ с console.anthropic.com
   - `GROUP_CHAT_ID` — `chat.id` новой группы (см. ниже, как получить)
4. Перед первым деплоем проверить актуальный ID модели Claude в
   docs.claude.com и при необходимости поправить `model` в `component.js`.

## Как получить `GROUP_CHAT_ID`

1. Добавить `@OzonAnnabot` в новую Telegram-группу с Евгением и Анной.
2. Отправить в группе любое сообщение с упоминанием `@OzonAnnabot`.
3. Выполнить:
   ```bash
   curl "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getUpdates"
   ```
4. В ответе найти `message.chat.id` этой группы (отрицательное число для
   групп) — это и есть `GROUP_CHAT_ID`.

## Настройка webhook (один раз, после получения URL от Pipedream)

```bash
curl -X POST "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook" \
  -d "url=<PIPEDREAM_WORKFLOW_URL>"
```

Проверка статуса вебхука в любой момент:
```bash
curl "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getWebhookInfo"
```

## Проверка (definition of done)

- [ ] Сообщение с `@OzonAnnabot` в группе → ответ в течение ~5-10 сек.
- [ ] Reply на сообщение бота → тоже получает ответ.
- [ ] Сообщения без упоминания/reply бот игнорирует.
- [ ] Личка с Анной (Ozon-эскалации) этой логикой не затронута.
- [ ] Токены/ключи нигде в коде — только в env vars Pipedream.

## Ограничения v1 (см. ТЗ, раздел 7)

- Без истории переписки — каждый ответ строится без контекста предыдущих
  сообщений группы (память — задача v2, по факту использования).
- Без rate-limit по частоте/бюджету запросов к Anthropic API (v2, если
  понадобится при активном использовании).

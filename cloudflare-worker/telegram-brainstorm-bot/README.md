# Telegram-бот для мозгового штурма — без Pipedream (Cloudflare Workers)

Тот же бот по ТЗ (`docs/tz_telegram_brainstorm_bot.md` — см. корень репозитория),
но webhook принимает напрямую Cloudflare Worker — без Pipedream и без
своего постоянно работающего сервера. Бесплатный тариф Workers (100k
запросов/сутки) с запасом покрывает нагрузку рабочей группы из двух человек.

Код: [`src/index.js`](./src/index.js).

## Деплой

Понадобится бесплатный аккаунт cloudflare.com.

```bash
cd cloudflare-worker/telegram-brainstorm-bot
npm install
npx wrangler login          # один раз, откроет браузер для авторизации
npx wrangler kv namespace create CHAT_HISTORY
                             # выведет id — вставить в wrangler.toml, в [[kv_namespaces]]
npx wrangler deploy         # публикует worker, выведет URL вида
                             # https://telegram-brainstorm-bot.<ваш-субдомен>.workers.dev
```

Задать секреты (спросит значение в интерактивном режиме, в код не попадают):

```bash
npx wrangler secret put TELEGRAM_BOT_TOKEN
npx wrangler secret put ANTHROPIC_API_KEY
npx wrangler secret put GROUP_CHAT_ID
```

Перед первым деплоем проверить актуальный ID модели Claude в
docs.claude.com и при необходимости поправить `model` в `src/index.js`,
затем повторить `npx wrangler deploy`.

## Как получить `GROUP_CHAT_ID`

1. Добавить `@OzonAnnabot` в новую Telegram-группу с Евгением и Анной.
2. Отправить в группе любое сообщение с упоминанием `@OzonAnnabot`.
3. Выполнить:
   ```bash
   curl "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getUpdates"
   ```
4. В ответе найти `message.chat.id` этой группы (отрицательное число для
   групп) — это и есть `GROUP_CHAT_ID`.

## Настройка webhook (один раз, после `wrangler deploy`)

```bash
curl -X POST "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook" \
  -d "url=https://telegram-brainstorm-bot.<ваш-субдомен>.workers.dev"
```

Проверка статуса вебхука в любой момент:
```bash
curl "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getWebhookInfo"
```

## Обновление кода после правок

```bash
npx wrangler deploy
```

Webhook URL не меняется — `setWebhook` повторно вызывать не нужно.

## Важно: Group Privacy mode бота

По умолчанию у Telegram-ботов включён Group Privacy mode — в этом режиме
бот вообще не получает обычные сообщения группы, даже с упоминанием себя
(только reply на свои сообщения и команды `/...`). Из-за этого webhook не
срабатывает, апдейты не долетают вообще (без ошибок — тихо теряются на
стороне Telegram).

Перед первым тестом отключить:
- `@BotFather` → `/mybots` → выбрать бота → «Bot Settings» → «Group Privacy» → «Turn off»
- Затем удалить бота из группы и добавить заново — иначе изменение может не применится к уже существующему членству.

## Память переписки

Бот хранит в Cloudflare KV (`CHAT_HISTORY`) последние 20 сообщений чата
(~10 обменов) и передаёт их в Anthropic API как контекст — учитывает,
что обсуждали раньше, не нужно каждый раз объяснять заново. Хранится
отдельно по `chat_id`. Старые сообщения за пределами лимита просто
обрезаются (без ошибок). Посмотреть/очистить память вручную:

```bash
npx wrangler kv key get "history:<GROUP_CHAT_ID>" --binding=CHAT_HISTORY --remote
npx wrangler kv key delete "history:<GROUP_CHAT_ID>" --binding=CHAT_HISTORY --remote
```

## Проверка (definition of done)

- [ ] Сообщение с `@OzonAnnabot` в группе → ответ в течение ~5-10 сек.
- [ ] Reply на сообщение бота → тоже получает ответ.
- [ ] Сообщения без упоминания/reply бот игнорирует.
- [ ] Личка с Анной (Ozon-эскалации) этой логикой не затронута.
- [ ] Токены/ключи нигде в коде — только `wrangler secret`.
- [ ] Бот помнит предыдущие сообщения в рамках последних ~10 обменов.

## Чем отличается от варианта на Pipedream

- Нет прослойки Pipedream — Telegram шлёт webhook прямо на Worker.
- Нет платного/лимитированного стороннего сервиса — Cloudflare Workers
  бесплатны в этом объёме нагрузки.
- Нужен `npx wrangler deploy` при каждом изменении кода (в Pipedream —
  правка прямо в веб-редакторе).
- Rate-limit по числу запросов к Anthropic API по-прежнему не сделан —
  см. ТЗ, раздел 7 (актуально, если объём переписки сильно вырастет).

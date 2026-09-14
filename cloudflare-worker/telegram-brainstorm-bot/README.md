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

## Проверка (definition of done)

- [ ] Сообщение с `@OzonAnnabot` в группе → ответ в течение ~5-10 сек.
- [ ] Reply на сообщение бота → тоже получает ответ.
- [ ] Сообщения без упоминания/reply бот игнорирует.
- [ ] Личка с Анной (Ozon-эскалации) этой логикой не затронута.
- [ ] Токены/ключи нигде в коде — только `wrangler secret`.

## Чем отличается от варианта на Pipedream

- Нет прослойки Pipedream — Telegram шлёт webhook прямо на Worker.
- Нет платного/лимитированного стороннего сервиса — Cloudflare Workers
  бесплатны в этом объёме нагрузки.
- Нужен `npx wrangler deploy` при каждом изменении кода (в Pipedream —
  правка прямо в веб-редакторе).
- Ограничения v1 (без истории переписки, без rate-limit) те же — см. ТЗ,
  раздел 7.

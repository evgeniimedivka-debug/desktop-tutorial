# Telegram-бот для мозгового штурма

Реализация бота-участника рабочей Telegram-группы (Евгений + Анна) для
мозгового штурма по бизнесу: Milis Cosmo, Milis Decor, art.Angel.
ТЗ: [`docs/tz_telegram_brainstorm_bot.md`](./docs/tz_telegram_brainstorm_bot.md).

Два равнозначных варианта деплоя — выбрать один:

- [`cloudflare-worker/telegram-brainstorm-bot/`](./cloudflare-worker/telegram-brainstorm-bot/)
  — без Pipedream, webhook принимает Cloudflare Worker напрямую. Бесплатно,
  без своего сервера. Рекомендуется.
- [`pipedream/telegram-brainstorm-bot/`](./pipedream/telegram-brainstorm-bot/)
  — исходный вариант из ТЗ, через Pipedream workflow.

Инструкции по деплою — в README внутри каждой папки.

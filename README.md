# Avito API — интеграция

Каркас для подключения магазина на Авито к Avito API: авторизация, синхронизация
цен/остатков объявлений, автоответы в мессенджере, статистика.

## Быстрый старт

```bash
pip install -r requirements.txt
cp .env.example .env   # заполнить AVITO_CLIENT_ID / AVITO_CLIENT_SECRET
python examples/check_auth.py
```

Как получить `client_id`/`client_secret` и что учесть по безопасности — см.
[`docs/AVITO_API_SETUP.md`](docs/AVITO_API_SETUP.md).

## Структура

- `avito_api/auth.py` — OAuth2 авторизация, автообновление токена
- `avito_api/client.py` — базовый HTTP-клиент
- `avito_api/autoload.py` — цены и статус объявлений
- `avito_api/messenger.py` — чаты, сообщения, автоответы
- `avito_api/stats.py` — статистика по объявлениям
- `examples/` — готовые скрипты запуска каждого сценария

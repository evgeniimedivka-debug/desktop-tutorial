"""Отправка готового ролика на утверждение в личный Telegram, ожидание ответа.

Использует raw Bot API через requests (без async-фреймворков) — проще держать
в одном стиле с остальным синхронным пайплайном.
"""
import time

import requests

TG_BASE = "https://api.telegram.org/bot{token}"

APPROVE_TEXT = "✅ Одобрить"
REJECT_TEXT = "❌ Отклонить"


def send_for_approval(config: dict, video_path: str, script: dict) -> int:
    """Отправляет видео + подпись с inline-кнопками. Возвращает message_id."""
    tg = config["telegram"]
    url = TG_BASE.format(token=tg["bot_token"]) + "/sendVideo"

    text = (
        f"Новый ролик на утверждение\n\n"
        f"Рубрика: {script['rubric']['name']}\n"
        f"Продукт: {script['idea']['product']}\n\n"
        f"Хук: {script['hook']}\n\n"
        f"Подпись к посту:\n{script['caption']}\n\n"
        f"Хэштеги: {' '.join(script['hashtags'])}"
    )
    keyboard = {
        "inline_keyboard": [
            [
                {"text": APPROVE_TEXT, "callback_data": "approve"},
                {"text": REJECT_TEXT, "callback_data": "reject"},
            ]
        ]
    }

    with open(video_path, "rb") as f:
        resp = requests.post(
            url,
            data={
                "chat_id": tg["chat_id"],
                "caption": text[:1024],
                "reply_markup": _to_json(keyboard),
            },
            files={"video": f},
            timeout=120,
        )
    resp.raise_for_status()
    return resp.json()["result"]["message_id"]


def wait_for_decision(config: dict, message_id: int, timeout_sec: int = 3600) -> str:
    """Поллинг getUpdates до нажатия кнопки под нужным сообщением.

    Возвращает "approve" или "reject". По таймауту — "reject" (ничего не публикуем).
    """
    tg = config["telegram"]
    base = TG_BASE.format(token=tg["bot_token"])
    deadline = time.time() + timeout_sec
    offset = None

    while time.time() < deadline:
        params = {"timeout": 20}
        if offset is not None:
            params["offset"] = offset
        resp = requests.get(f"{base}/getUpdates", params=params, timeout=30)
        resp.raise_for_status()
        for update in resp.json().get("result", []):
            offset = update["update_id"] + 1
            callback = update.get("callback_query")
            if not callback:
                continue
            if callback["message"]["message_id"] != message_id:
                continue
            decision = callback["data"]
            requests.post(
                f"{base}/answerCallbackQuery",
                data={"callback_query_id": callback["id"]},
                timeout=15,
            )
            return decision
    return "reject"


def _to_json(obj) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False)

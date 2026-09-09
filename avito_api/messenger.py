from .client import AvitoClient

# Как и в autoload.py — сверьте версии эндпоинтов (v1/v2/v3) с разделом
# "Мессенджер" в каталоге API вашего кабинета перед первым запуском.


class MessengerAPI:
    """Чтение и отправка сообщений, автоответы в мессенджере Avito."""

    def __init__(self, client: AvitoClient):
        self.client = client
        self._user_id: int | None = None

    def _account_id(self) -> int:
        if self._user_id is None:
            self._user_id = self.client.whoami()["id"]
        return self._user_id

    def list_chats(self, unread_only: bool = False, limit: int = 50) -> list[dict]:
        params = {"unread_only": str(unread_only).lower(), "limit": limit}
        resp = self.client.get(f"/messenger/v2/accounts/{self._account_id()}/chats", params=params)
        return resp.json().get("chats", [])

    def list_messages(self, chat_id: str, limit: int = 50) -> list[dict]:
        resp = self.client.get(
            f"/messenger/v3/accounts/{self._account_id()}/chats/{chat_id}/messages/",
            params={"limit": limit},
        )
        return resp.json()

    def send_message(self, chat_id: str, text: str) -> dict:
        payload = {"message": {"text": text}, "type": "text"}
        resp = self.client.post(
            f"/messenger/v1/accounts/{self._account_id()}/chats/{chat_id}/messages",
            json=payload,
        )
        return resp.json()

    def mark_read(self, chat_id: str) -> None:
        self.client.post(f"/messenger/v1/accounts/{self._account_id()}/chats/{chat_id}/read")

    def auto_reply_to_new_messages(self, reply_text: str) -> int:
        """
        Простейший автоответ: проходит по непрочитанным чатам и отправляет
        reply_text один раз в каждый. Для боевого использования нужна
        персистентность (не отвечать повторно) и, в идеале, вебхук вместо
        поллинга — см. раздел "Вебхуки" в документации мессенджера.
        """
        chats = self.list_chats(unread_only=True)
        for chat in chats:
            self.send_message(chat["id"], reply_text)
            self.mark_read(chat["id"])
        return len(chats)

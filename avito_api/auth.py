import time
import threading

import requests

from .config import AvitoConfig

TOKEN_URL_PATH = "/token"


class AvitoAuth:
    """
    OAuth2 client_credentials авторизация для Avito API.

    Документация: раздел "Авторизация" в каталоге API вашего кабинета
    (Мои приложения -> ваше приложение -> Client ID / Client Secret).
    Токен живёт ограниченное время (обычно порядка суток) — класс сам
    обновляет его перед истечением.
    """

    def __init__(self, config: AvitoConfig):
        self._config = config
        self._access_token: str | None = None
        self._expires_at: float = 0.0
        self._lock = threading.Lock()

    def get_token(self) -> str:
        with self._lock:
            if self._access_token is None or time.time() >= self._expires_at:
                self._refresh()
            return self._access_token

    def _refresh(self) -> None:
        url = f"{self._config.base_url}{TOKEN_URL_PATH}"
        response = requests.post(
            url,
            data={
                "grant_type": "client_credentials",
                "client_id": self._config.client_id,
                "client_secret": self._config.client_secret,
            },
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()

        self._access_token = payload["access_token"]
        expires_in = payload.get("expires_in", 3600)
        # обновляем токен на минуту раньше фактического истечения
        self._expires_at = time.time() + expires_in - 60

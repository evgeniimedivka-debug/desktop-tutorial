import requests

from .auth import AvitoAuth
from .config import AvitoConfig


class AvitoClient:
    """Базовый HTTP-клиент Avito API: авторизация + общие запросы."""

    def __init__(self, config: AvitoConfig | None = None):
        self.config = config or AvitoConfig.from_env()
        self.auth = AvitoAuth(self.config)
        self._session = requests.Session()

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.config.base_url}{path}"
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.auth.get_token()}"

        response = self._session.request(method, url, headers=headers, timeout=30, **kwargs)

        if response.status_code == 401:
            # токен могли отозвать досрочно — обновляем один раз и повторяем
            self.auth._expires_at = 0
            headers["Authorization"] = f"Bearer {self.auth.get_token()}"
            response = self._session.request(method, url, headers=headers, timeout=30, **kwargs)

        response.raise_for_status()
        return response

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def patch(self, path: str, **kwargs) -> requests.Response:
        return self.request("PATCH", path, **kwargs)

    def whoami(self) -> dict:
        """Данные текущего аккаунта — удобно для проверки, что авторизация настроена верно."""
        return self.get("/core/v1/accounts/self").json()

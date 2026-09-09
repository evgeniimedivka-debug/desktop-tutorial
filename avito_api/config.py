import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AvitoConfig:
    client_id: str
    client_secret: str
    base_url: str = "https://api.avito.ru"

    @classmethod
    def from_env(cls) -> "AvitoConfig":
        client_id = os.environ.get("AVITO_CLIENT_ID")
        client_secret = os.environ.get("AVITO_CLIENT_SECRET")
        if not client_id or not client_secret:
            raise RuntimeError(
                "AVITO_CLIENT_ID / AVITO_CLIENT_SECRET не заданы. "
                "Скопируйте .env.example в .env и заполните значениями из кабинета Avito."
            )
        return cls(client_id=client_id, client_secret=client_secret)

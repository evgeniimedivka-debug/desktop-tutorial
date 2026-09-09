"""
Быстрая проверка, что авторизация настроена верно.

Запуск:
    cp .env.example .env      # и заполните значениями из кабинета Avito
    pip install -r requirements.txt
    python examples/check_auth.py
"""

from dotenv import load_dotenv

from avito_api import AvitoClient

load_dotenv()

client = AvitoClient()
me = client.whoami()
print("Авторизация успешна. Аккаунт:", me)

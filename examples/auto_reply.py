"""
Пример: разослать автоответ во все непрочитанные чаты мессенджера.
Для регулярного запуска повесьте этот скрипт на cron / планировщик задач.
"""

from dotenv import load_dotenv

from avito_api import AvitoClient
from avito_api.messenger import MessengerAPI

load_dotenv()

REPLY_TEXT = "Спасибо за сообщение! Отвечу в течение часа."

client = AvitoClient()
messenger = MessengerAPI(client)

count = messenger.auto_reply_to_new_messages(REPLY_TEXT)
print(f"Отправлено автоответов: {count}")

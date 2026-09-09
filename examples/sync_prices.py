"""
Пример: синхронизация цен объявлений по словарю {item_id: цена}.
Замените словарь ITEM_PRICES на выгрузку из своей учётной системы
(Excel/1С/Google Sheets — как вам удобнее подготовить данные).
"""

from dotenv import load_dotenv

from avito_api import AvitoClient
from avito_api.autoload import AutoloadAPI

load_dotenv()

ITEM_PRICES = {
    # 123456789: 4500,
}

client = AvitoClient()
autoload = AutoloadAPI(client)

results = autoload.sync_from_mapping(ITEM_PRICES)
for item_id, status in results.items():
    print(item_id, "->", status)

"""Пример: статистика по объявлениям за последние 7 дней."""

from datetime import date, timedelta

from dotenv import load_dotenv

from avito_api import AvitoClient
from avito_api.stats import StatsAPI

load_dotenv()

ITEM_IDS = [
    # 123456789,
]

client = AvitoClient()
stats = StatsAPI(client)

data = stats.get_items_stats(
    item_ids=ITEM_IDS,
    date_from=date.today() - timedelta(days=7),
    date_to=date.today(),
)
print(data)

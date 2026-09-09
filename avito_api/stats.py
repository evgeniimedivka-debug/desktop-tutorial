from datetime import date

from .client import AvitoClient

# Сверьте эндпоинт и допустимые поля (fields) со Stats API в вашем кабинете —
# набор метрик и лимит на количество item_ids за один запрос могут отличаться.


class StatsAPI:
    """Статистика по объявлениям: просмотры, контакты, избранное."""

    def __init__(self, client: AvitoClient):
        self.client = client
        self._user_id: int | None = None

    def _account_id(self) -> int:
        if self._user_id is None:
            self._user_id = self.client.whoami()["id"]
        return self._user_id

    def get_items_stats(
        self,
        item_ids: list[int],
        date_from: date,
        date_to: date,
        fields: tuple[str, ...] = ("uniqViews", "uniqContacts", "uniqFavorites"),
        period_grouping: str = "day",
    ) -> dict:
        payload = {
            "dateFrom": date_from.isoformat(),
            "dateTo": date_to.isoformat(),
            "itemIds": item_ids,
            "fields": list(fields),
            "periodGrouping": period_grouping,
        }
        resp = self.client.post(f"/stats/v1/accounts/{self._account_id()}/items", json=payload)
        return resp.json()

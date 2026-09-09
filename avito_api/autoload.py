from .client import AvitoClient

# ВАЖНО: точные пути эндпоинтов и набор доступных операций зависят от того,
# какие продукты API включены для вашего аккаунта (раздел "Каталог API" в
# кабинете). Ниже — базовая реализация по актуальной на момент написания
# документации Avito; перед первым запуском сверьте пути и структуру
# ответа с разделом "Управление объявлениями" / "Автозагрузка" в вашем
# кабинете и поправьте при расхождениях.


class AutoloadAPI:
    """Обновление цены и статуса (активно/снято) объявлений без полной перезаливки фида."""

    def __init__(self, client: AvitoClient):
        self.client = client

    def update_price(self, item_id: int, price: int) -> dict:
        """Установить новую цену объявления (в рублях, целое число)."""
        payload = {"price": price}
        return self.client.patch(f"/core/v1/items/{item_id}", json=payload).json()

    def set_availability(self, item_id: int, available: bool) -> dict:
        """available=False снимает объявление с публикации, True — восстанавливает."""
        payload = {"status": "active" if available else "removed"}
        return self.client.patch(f"/core/v1/items/{item_id}", json=payload).json()

    def get_report_status(self, report_id: int) -> dict:
        """Статус обработки фида, загруженного через Автозагрузку."""
        return self.client.get(f"/autoload/v2/reports/{report_id}/items").json()

    def sync_from_mapping(self, price_by_item_id: dict[int, int]) -> dict[int, str]:
        """
        Массовое обновление цен по словарю {item_id: новая_цена}.
        Возвращает {item_id: "ok" | текст ошибки} — для логирования результата синхронизации.
        """
        results: dict[int, str] = {}
        for item_id, price in price_by_item_id.items():
            try:
                self.update_price(item_id, price)
                results[item_id] = "ok"
            except Exception as exc:  # логируем и идём дальше, не прерывая всю синхронизацию
                results[item_id] = str(exc)
        return results

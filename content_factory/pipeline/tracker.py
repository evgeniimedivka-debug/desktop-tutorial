"""Запись статуса ролика в лист "Контент-план" xlsx-трекера."""
import datetime

from openpyxl import load_workbook

STATUS_COL = 6      # "Статус"
LINK_COL = 7        # "Ссылка на ролик"
COMMENT_COL = 12     # "Комментарий"


def log_result(xlsx_path: str, product: str, rubric_name: str, status: str,
                link: str = "", comment: str = "") -> None:
    """Находит первую пустую/подходящую строку по продукту+рубрике и обновляет статус.

    Если готовой строки под сегодняшнюю дату нет — добавляет новую в конец.
    """
    wb = load_workbook(xlsx_path)
    ws = wb["Контент-план"]

    today = datetime.date.today().strftime("%d.%m.%Y")
    target_row = None
    for row in range(2, ws.max_row + 1):
        if ws.cell(row=row, column=4).value == product and \
           ws.cell(row=row, column=3).value == rubric_name and \
           ws.cell(row=row, column=6).value in ("Идея", "Сценарий", "Съёмка", "Монтаж"):
            target_row = row
            break

    if target_row is None:
        target_row = ws.max_row + 1
        ws.cell(row=target_row, column=1, value=today)
        ws.cell(row=target_row, column=3, value=rubric_name)
        ws.cell(row=target_row, column=4, value=product)
        ws.cell(row=target_row, column=5, value="ИИ")

    ws.cell(row=target_row, column=STATUS_COL, value=status)
    if link:
        ws.cell(row=target_row, column=LINK_COL, value=link)
    if comment:
        ws.cell(row=target_row, column=COMMENT_COL, value=comment)

    wb.save(xlsx_path)

r"""
**Задача 10 (Excel и JSON).** Сохраните DataFrame в Excel с двумя листами (`Cars`, `Customers`) через `ExcelWriter`. Прочитайте через `sheet_name=None` — получите словарь; проверьте `type()` и `keys()`. Прочитайте только `Cars`. Сохраните в JSON через `to_json(orient="records", lines=True)` и прочитайте через `read_json(lines=True)`. Создайте вложенный JSON (с `address` и `orders`) и нормализуйте через `pd.json_normalize()`. Ожидаемый вывод: `sheet_name=None` возвращает `dict` с ключами `["Cars", "Customers"]`; `json_normalize` с `record_path="orders"` разворачивает вложенный список в строки; `max_level=1` останавливает нормализацию на первом уровне. В комментариях объясните: в каких случаях `json_normalize` необходим (ответы API автосалона с вложенностью); как `record_path` разворачивает вложенный список (каждый элемент — строка); почему `orient="records"` удобнее для API (список объектов); чем `lines=True` отличается от обычного JSON (NDJSON — по одному объекту на строку); как `max_level` ограничивает глубину нормализации; какие типы Excel сохраняет, а какие теряет (теряет `category`, `datetime` с таймзоной, длинные ID > 15 цифр).
"""
import json
import pandas as pd
from pathlib import Path

HERE = Path(__file__).parent
cars = pd.DataFrame({"vin": ["V1", "V2"], "model": ["Camry", "X5"], "price": [2.5e6, 5.5e6]})
customers = pd.DataFrame({"id": [1, 2, 3], "name": ["Анна", "Борис", "Вера"]})
xlsx = HERE / "autosalon.xlsx"
with pd.ExcelWriter(xlsx) as w:
    cars.to_excel(w, sheet_name="Cars", index=False)
    customers.to_excel(w, sheet_name="Customers", index=False)
d = pd.read_excel(xlsx, sheet_name=None)
print(type(d).__name__, list(d.keys()))
print(pd.read_excel(xlsx, sheet_name="Cars"))

js = HERE / "cars.jsonl"
cars.to_json(js, orient="records", lines=True)
print(js.read_text().strip().splitlines()[0], "\n", pd.read_json(js, lines=True))
nested = [{"id": 1, "name": "Анна", "address": {"city": "Москва", "zip": "101000"},
           "orders": [{"vin": "V1", "sum": 2500000}, {"vin": "V2", "sum": 1800000}]},
          {"id": 2, "name": "Борис", "address": {"city": "СПб", "zip": "190000"}, "orders": [{"vin": "V3", "sum": 950000}]}]
print(pd.json_normalize(nested, record_path="orders", meta=["id", "name", ["address", "city"]]))
print("max_level=1:", pd.json_normalize(nested, max_level=1).columns.tolist())
xlsx.unlink(); js.unlink()
# sheet_name=None -> словарь {имя листа: DataFrame}. json_normalize нужен для вложенных ответов API:
# record_path разворачивает вложенный СПИСОК (каждый элемент -> строка), meta добавляет поля родителя,
# max_level ограничивает глубину «разглаживания» словарей. orient="records" - список объектов
# (удобно для API); lines=True - NDJSON (по объекту на строку, можно читать потоково).
# Excel теряет: category, datetime с таймзоной, а длинные числа (>15 цифр, ID) округляются до 15 значащих.

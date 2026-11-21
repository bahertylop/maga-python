r"""
**Задача 20 (duplicated/drop_duplicates/replace).** Создайте DataFrame продаж с дубликатами. Проверьте `duplicated()`, `duplicated(subset=["sale_id"])`, `duplicated(keep=False)`. Удалите через `drop_duplicates()`, `keep="last"`, `keep=False`, `subset=["sale_id"]`. Примените `replace(1, 100)`, `replace([1, 2], [100, 200])`, `replace({"старый": "новый"})`. Ожидаемый вывод: `duplicated()` возвращает `[False, False, True, ...]`; `keep=False` помечает все вхождения; `drop_duplicates(subset=["sale_id"])` удаляет по ключу. В комментариях объясните: чем `keep=False` отличается от `keep="first"` (`False` удаляет все дубликаты, `"first"` оставляет первый); в каких случаях `subset` важнее полного сравнения строк (когда есть служебные столбцы с датой/временем продажи); как `replace` работает с `regex=True` (регулярные выражения); что произойдёт при `replace` значения, отсутствующего в данных (ничего, без ошибки); как `replace` со словарём обрабатывает отсутствующие ключи (игнорирует); чем `replace` отличается от `map` (`map` заменяет все значения, отсутствующие → `NaN`; `replace` — только указанные).
"""
import pandas as pd

df = pd.DataFrame({"sale_id": [1, 2, 2, 3, 3, 3], "brand": ["Kia", "BMW", "BMW", "Kia", "Kia", "Toyota"],
                   "ts": ["10:00", "11:00", "11:05", "12:00", "12:01", "13:00"]})
print("duplicated():", df.duplicated().tolist())
print("subset sale_id:", df.duplicated(subset=["sale_id"]).tolist(), "| keep=False:", df.duplicated(subset=["sale_id"], keep=False).tolist())
print("drop_duplicates(subset=sale_id):", df.drop_duplicates(subset=["sale_id"]).index.tolist(),
      "| keep='last':", df.drop_duplicates(subset=["sale_id"], keep="last").index.tolist(),
      "| keep=False:", df.drop_duplicates(subset=["sale_id"], keep=False).index.tolist())
n = pd.Series([1, 2, 3, 1])
print("replace(1,100):", n.replace(1, 100).tolist(), "| списки:", n.replace([1, 2], [100, 200]).tolist(), "| нет значения:", n.replace(99, 0).tolist())
print("dict:", pd.Series(["старый", "x"]).replace({"старый": "новый"}).tolist())
print("regex:", pd.Series(["Camry-2020", "Rio-2019"]).replace(r"-\d+", "", regex=True).tolist())
# keep=False помечает/удаляет ВСЕ копии (не остаётся ни одной), keep="first" оставляет первую. subset важнее полного сравнения,
# когда есть служебные столбцы (время продажи, id записи), из-за которых строки «не равны» формально. replace с regex=True
# понимает регулярки; значения, которых нет в данных, игнорируются без ошибки; replace трогает только указанное,
# а map заменяет ВСЕ значения (отсутствующие ключи -> NaN).

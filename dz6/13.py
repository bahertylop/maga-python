r"""
**Задача 13 (index: set_index, reset_index, MultiIndex).** Создайте DataFrame из 20 автомобилей с `vin`, `price`, `brand`. Установите `vin` как индекс через `set_index`. Верните обратно через `reset_index()` и `reset_index(drop=True)`. Создайте MultiIndex через `set_index(["brand", "vin"])`. Выполните выборку: `df.loc["Toyota"]`, `df.xs("Toyota", level="brand")`. Создайте DataFrame с дубликатами индекса `["a", "b", "a", "c"]` — проверьте `index.is_unique`, `index.duplicated()`, `df.loc["a"]`. Ожидаемый вывод: `reset_index()` создаёт столбец `vin` и `RangeIndex`, `reset_index(drop=True)` — только `RangeIndex`; `df.loc["a"]` с дубликатами возвращает две строки; `index.is_unique = False`, `duplicated() = [False, False, True, False]`. В комментариях объясните: чем `drop=True/False` различаются; как `xs` с `drop_level=False` сохраняет уровень; почему `.loc` с дубликатами возвращает несколько строк; как MultiIndex влияет на `groupby` (группировка по бренду и VIN); что произойдёт при `xs` с несуществующим уровнем (`KeyError`); зачем нужен `allows_duplicate_labels=False` (защита от случайных дубликатов VIN).
"""
import pandas as pd

brands = ["Toyota", "BMW", "Kia", "Hyundai"]
df = pd.DataFrame({"vin": [f"VIN{i:03d}" for i in range(20)], "price": [1_000_000 + 90_000 * i for i in range(20)],
                   "brand": [brands[i % 4] for i in range(20)]})
by_vin = df.set_index("vin")
print(by_vin.reset_index().columns.tolist(), "| drop=True:", by_vin.reset_index(drop=True).columns.tolist())
multi = df.set_index(["brand", "vin"]).sort_index()
print("loc['Toyota']:", len(multi.loc["Toyota"]), "строк | xs:", len(multi.xs("Toyota", level="brand")))
print("xs drop_level=False сохраняет уровень:", multi.xs("Toyota", level="brand", drop_level=False).index.names)
try:
    multi.xs("Toyota", level="нет_такого")
except Exception as e:
    print("xs несуществующий уровень ->", type(e).__name__, e)
dup = pd.DataFrame({"v": [1, 2, 3, 4]}, index=["a", "b", "a", "c"])
print("is_unique:", dup.index.is_unique, "| duplicated:", dup.index.duplicated().tolist(), "| loc['a'] строк:", len(dup.loc["a"]))
try:
    dup.set_flags(allows_duplicate_labels=False)
except Exception as e:
    print("allows_duplicate_labels=False ->", type(e).__name__)
print("groupby по MultiIndex-уровню:", multi.groupby(level="brand")["price"].mean().round(0).to_dict())
# drop=True отбрасывает старый индекс, drop=False (по умолчанию) переносит его в столбец. .loc с дублирующейся меткой
# возвращает ВСЕ строки с ней (DataFrame, а не скаляр). allows_duplicate_labels=False защитит от случайных
# дубликатов VIN: попытка создать/добавить дубль даст DuplicateLabelError.

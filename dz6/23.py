r"""
**Задача 23 (.str.split/extract).** Создайте Series имён клиентов `"Анна Иванова"`. Примените `.str.split(expand=True)` — получите DataFrame с двумя столбцами. Примените `.str.split("-", n=1, expand=True)` к строкам с дефисом (например, "Иванов-Петров") и `.str.rsplit("-", n=1, expand=True)`. Создайте Series дат продаж `"2025-01-15"`. Извлеките год, месяц, день через `.str.extract(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})")`. Примените `.str.extractall(r"(\d)")` и `.str.findall(r"\d+")`. Ожидаемый вывод: `split(expand=True)` возвращает DataFrame 10×2; `extract` с именованными группами возвращает DataFrame с колонками `year`, `month`, `day`; `extractall` возвращает MultiIndex. В комментариях объясните: зачем `expand=True` (возвращает DataFrame вместо Series списков); как именованные группы делают код читаемее; чем `extract` отличается от `extractall` (первое совпадение vs все совпадения); как `n=1` ограничивает разделения (разделить только один раз); что произойдёт при `extract` без групп (возвращает одну колонку с полным совпадением); как `findall` обрабатывает несколько совпадений (возвращает список).
"""
import pandas as pd

names = pd.Series(["Анна Иванова", "Борис Петров", "Вера Сидорова"])
print(names.str.split(expand=True))
print("n=1:\n", pd.Series(["Иванов-Петров-Сидоров"]).str.split("-", n=1, expand=True))
print("rsplit n=1:\n", pd.Series(["Иванов-Петров-Сидоров"]).str.rsplit("-", n=1, expand=True))
dates = pd.Series(["2025-01-15", "2025-02-20"])
print(dates.str.extract(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"))
print("extractall:\n", pd.Series(["a1b22"]).str.extractall(r"(\d)"))
print("findall:", pd.Series(["a1b22", "c333"]).str.findall(r"\d+").tolist())
print("extract без групп ->", end=" ")
try:
    print(dates.str.extract(r"\d{4}"))
except ValueError as e:
    print(type(e).__name__, e)
# expand=True возвращает DataFrame (иначе - Series списков). Именованные группы (?P<имя>...) становятся именами столбцов.
# extract берёт ПЕРВОЕ совпадение, extractall - все (результат с MultiIndex (строка, номер совпадения)).
# n=1 ограничивает число разбиений. extract требует хотя бы одной группы захвата (иначе ValueError). findall возвращает список совпадений.

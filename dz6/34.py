r"""
**Задача 34 (date_range, DatetimeIndex, .dt).** Создайте `pd.date_range("2024-01-01", periods=365, freq="D")`. Создайте диапазоны с `freq="B"`, `"ME"`, `"YE"`, `"h"`. Установите `DatetimeIndex` как индекс. Выполните `df["2024"]`, `df["2024-01"]`, `df["2024-01-15"]`, `df["2024-01-01":"2024-01-31"]`. Примените `.dt.year`, `.dt.month`, `.dt.day_name()`, `.dt.to_period("M")`. Ожидаемый вывод: `freq="B"` даёт 260 рабочих дней в году; `freq="ME"` — конец каждого месяца; `df["2024-01"]` возвращает 31 строку; `.dt.day_name()` возвращает день недели. В комментариях объясните: почему `freq="ME"` вместо `"M"` в Pandas 3.0 (унификация с `"YE"`, `"QE"`); как `df["2024-01"]` работает без `.loc` (частичная индексация по `DatetimeIndex`); когда `.dt` незаменим (извлечение компонент даты); чем частичная индексация отличается от `.loc` (более лаконичный синтаксис); что произойдёт при `df["2024-13"]` (`KeyError` или пустой результат); как `date_range` обрабатывает високосные годы (29 февраля включается при `freq="D"`).
"""
import numpy as np
import pandas as pd

d = pd.date_range("2024-01-01", periods=365, freq="D")
print("freq B:", len(pd.date_range("2024-01-01", "2024-12-31", freq="B")), "рабочих дней | ME:", len(pd.date_range("2024-01-01", "2024-12-31", freq="ME")),
      "| YE:", pd.date_range("2024-01-01", periods=2, freq="YE").tolist()[0].date(), "| h:", len(pd.date_range("2024-01-01", periods=24, freq="h")))
print("високосный год:", len(pd.date_range("2024-01-01", "2024-12-31")), "дней; 29 февраля есть:", pd.Timestamp("2024-02-29") in d)
df = pd.DataFrame({"sales": np.arange(365)}, index=d)
print(".loc['2024-01']:", len(df.loc["2024-01"]), "| .loc['2024']:", len(df.loc["2024"]), "| .loc['2024-01-15']:", df.loc["2024-01-15"].iloc[0])
print("срез:", len(df.loc["2024-01-01":"2024-01-31"]))
try:
    print("df['2024-01'] без .loc:", len(df["2024-01"]))
except KeyError as e:
    print("df['2024-01'] в Pandas 3 -> KeyError (используйте .loc)")
try:
    df.loc["2024-13"]
except (KeyError, ValueError) as e:
    print("'2024-13' ->", type(e).__name__)
s = df.reset_index(names="date")["date"]
print(s.dt.year.iloc[0], s.dt.month.iloc[0], s.dt.day_name().iloc[0], s.dt.to_period("M").iloc[0])
# В Pandas 3.0 частоты "ME"/"YE"/"QE" (конец периода) отличаются от "MS"/"YS"/"QS" (начало); одиночные "M"/"Y" убраны, чтобы
# не путать начало и конец. Частичная индексация строкой ("2024-01") выбирает все строки периода; для строк DataFrame
# её нужно писать через .loc. .dt - извлечение компонент из СТОЛБЦА дат. "2024-13" - несуществующий месяц.

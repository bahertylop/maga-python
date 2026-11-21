r"""
**Задача 5 (arange, linspace, date_range, CSV).** Сгенерируйте DataFrame из 50 продаж: `sale_id`, `sale_date` (2000–2025), `amount`. Создайте `pd.Series(np.arange(2000, 2026))` и `pd.Series(np.linspace(500000, 5000000, 10))` (суммы сделок). Сохраните DataFrame в `sales.csv` через `to_csv(index=False)` и прочитайте обратно с `parse_dates=["sale_date"]`, `usecols=["sale_id", "amount"]`, `nrows=10`. Проверьте `len(np.arange(0, 1, 0.1))` и сравните с `len(np.linspace(0, 1, 10))`. Ожидаемый вывод: `len(np.arange(0, 1, 0.1))` может вернуть 10 или 9 (зависит от платформы, из-за погрешности float); `len(np.linspace(0, 1, 10)) = 10` всегда. В комментариях объясните: почему `linspace` надёжнее при фиксированной длине; как `index=False` влияет на структуру CSV (не записывается лишний столбец с индексом); зачем `parse_dates` при чтении (превращает строку в `datetime64`); почему `freq="YE"` вместо `freq="Y"` в Pandas 3.0; как `usecols` экономит память (читает только нужные столбцы); что произойдёт при чтении CSV без `dtype` для числовых столбцов (Pandas угадает `int64`/`float64`, но может ошибиться, если есть пропуски).
"""
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(5)
HERE = Path(__file__).parent
dates = pd.to_datetime(rng.integers(pd.Timestamp("2000-01-01").value // 10**9, pd.Timestamp("2025-12-31").value // 10**9, 50), unit="s").normalize()
df = pd.DataFrame({"sale_id": np.arange(1, 51), "sale_date": dates, "amount": rng.uniform(5e5, 5e6, 50).round(0)})
years = pd.Series(np.arange(2000, 2026)); amounts = pd.Series(np.linspace(500000, 5000000, 10))
print(len(years), len(amounts), "| годовой диапазон:", len(pd.date_range("2000", periods=26, freq="YE")))

csv = HERE / "sales.csv"
df.to_csv(csv, index=False)             # index=False: без лишнего столбца Unnamed: 0
try:
    pd.read_csv(csv, parse_dates=["sale_date"], usecols=["sale_id", "amount"], nrows=10)
except ValueError as e:
    print("parse_dates + usecols без sale_date ->", e)      # столбец в parse_dates обязан быть в usecols
back = pd.read_csv(csv, parse_dates=["sale_date"], usecols=["sale_id", "sale_date", "amount"], nrows=10)
print(back.dtypes.to_dict())
print("len(arange(0,1,0.1)) =", len(np.arange(0, 1, 0.1)), "| len(linspace(0,1,10)) =", len(np.linspace(0, 1, 10)))
# linspace надёжнее при фиксированной длине: точки считаются от числа точек, а не накоплением float-шага.
# (arange(0, 1, 0.1) обычно даёт 10; расхождения на ±1 бывают на других границах, напр. arange(0.1, 0.4, 0.1).)
# parse_dates превращает строку в datetime64 (иначе дата останется str - нет .dt, resample, сортировки по времени).
# В Pandas 3.0 частота года - "YE" ("Y" больше не поддерживается), месяц - "ME", квартал - "QE".
# usecols читает только нужные столбцы - экономит память и время. Без dtype Pandas угадывает
# типы: int64/float64, а при пропусках целый столбец превращается во float64.
csv.unlink()

r"""
**Задача 48 (df.plot: scatter/box/area/pie).** Примените `df.plot(kind="scatter", x="price", y="cost", alpha=0.5)`, `df.plot(kind="box")`, `customers.boxplot(column="age", by="city")`, `df.plot(kind="area", stacked=True)`, `status_counts.plot(kind="pie", autopct="%1.1f%%")`. Ожидаемый вывод: `scatter` показывает связь двух переменных; `box` — квартили и выбросы; `area(stacked=True)` — накопленные доли; `pie` — доли от целого. В комментариях объясните: когда `box` лучше `hist` (сравнение групп, выбросы); почему `pie` плохо работает с >7 категорий (нечитаемость); как `stacked=True` в `area` показывает доли; что произойдёт при `scatter` без `x`/`y` (`ValueError`); как `boxplot(by=...)` группирует данные; почему `pie` требует один столбец.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

rng = np.random.default_rng(48)
n = 300
df = pd.DataFrame({"price": rng.normal(2.5e6, 5e5, n)}); df["cost"] = df["price"] * 0.8 + rng.normal(0, 8e4, n)
customers = pd.DataFrame({"age": rng.integers(18, 70, n), "city": rng.choice(["Москва", "СПб", "Казань"], n)})
area = pd.DataFrame(rng.integers(5, 20, (12, 3)).astype(float), columns=["седан", "SUV", "хэтч"], index=pd.date_range("2025-01-01", periods=12, freq="MS"))
status = pd.Series({"completed": 70, "cancelled": 15, "pending": 15})
fig, axes = plt.subplots(2, 3, figsize=(16, 8))
df.plot(kind="scatter", x="price", y="cost", alpha=0.5, ax=axes[0, 0], title="scatter")
df.plot(kind="box", ax=axes[0, 1], title="box")
customers.boxplot(column="age", by="city", ax=axes[0, 2]); axes[0, 2].set_title("boxplot by city")
area.plot(kind="area", stacked=True, ax=axes[1, 0], title="area stacked")
(area.div(area.sum(axis=1), axis=0)).plot(kind="area", stacked=True, ax=axes[1, 1], title="area: доли (сумма=1)")
status.plot(kind="pie", autopct="%1.1f%%", ax=axes[1, 2], title="pie", ylabel="")
fig.suptitle(""); fig.tight_layout(); fig.savefig(Path(__file__).parent / "48_charts.png", dpi=80); plt.close(fig)
print("график сохранён: 48_charts.png")
try:
    df.plot(kind="scatter")
except ValueError as e:
    print("scatter без x/y ->", type(e).__name__, "-", e)
try:
    pd.DataFrame({"a": [1, 2], "b": [3, 4]}).plot(kind="pie")
except ValueError as e:
    print("pie для DataFrame без y ->", e)
plt.close("all")
# box лучше hist для сравнения нескольких групп и поиска выбросов: компактно показывает медиану, квартили, «усы» (1.5*IQR) и точки-выбросы.
# pie плохо читается при >7 категорий: мелкие доли сливаются, углы трудно сравнивать (лучше barh с сортировкой).
# area(stacked=True) накладывает ряды друг на друга: высота = сумма; для ДОЛЕЙ нормируйте строки на сумму (график справа).
# scatter без x и y -> ValueError (нужны обе оси). boxplot(by="city") группирует значения age по городам, по одной коробке на группу.
# pie рисует ОДНУ величину (доли от целого), поэтому нужен Series либо y= столбца DataFrame.

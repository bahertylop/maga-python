r"""
**Задача 47 (df.plot: line/bar/barh/hist).** Создайте DataFrame с временным рядом продаж. Постройте `df.plot(kind="line", figsize=(12, 6), title="...")`, `df.plot(kind="bar", x="brand", y="sales")`, `df.plot(kind="barh", ...)`, `df["price"].plot(kind="hist", bins=20)`. Примените `xlabel`, `ylabel`, `grid`, `color`, `alpha`, `legend`. Ожидаемый вывод: `line` рисует линию по индексу; `bar` — вертикальные столбцы; `barh` — горизонтальные; `hist` — распределение с `bins` интервалами. В комментариях объясните: когда `barh` удобнее `bar` (длинные названия брендов); зачем `bins` в гистограмме (число интервалов); как `alpha` влияет на читаемость (прозрачность); что произойдёт при `plot` без `figsize` (размер по умолчанию); как `legend` управляет подписями; почему `hist` работает только с одним столбцом (распределение одной переменной).
"""
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path

rng = np.random.default_rng(47)
ts = pd.DataFrame({"Toyota": rng.normal(100, 10, 12).cumsum(), "BMW": rng.normal(80, 10, 12).cumsum()}, index=pd.date_range("2025-01-01", periods=12, freq="MS"))
ax = ts.plot(kind="line", figsize=(12, 6), title="Продажи по месяцам", xlabel="Месяц", ylabel="Продажи, шт.", grid=True, alpha=0.9, legend=True)
ax.figure.savefig(Path(__file__).parent / "47_line.png", dpi=80); plt.close("all")
brands = pd.DataFrame({"brand": ["Mercedes-Benz E-Class", "Volkswagen Tiguan", "Kia Rio", "Lada Vesta"], "sales": [30, 55, 70, 40]})
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
brands.plot(kind="bar", x="brand", y="sales", ax=axes[0], color="tab:blue", title="bar", legend=False, rot=30)
brands.plot(kind="barh", x="brand", y="sales", ax=axes[1], color="tab:green", title="barh", legend=False)
pd.DataFrame({"price": rng.normal(2.5e6, 6e5, 1000)})["price"].plot(kind="hist", bins=20, ax=axes[2], alpha=0.7, title="hist", xlabel="Цена")
fig.tight_layout(); fig.savefig(Path(__file__).parent / "47_charts.png", dpi=80)
print("графики сохранены: 47_line.png, 47_charts.png; размер по умолчанию:", matplotlib.rcParams["figure.figsize"])
try:
    pd.DataFrame({"a": [1, 2], "b": [3, 4]}).plot(kind="hist", y=["a", "b"], bins=2)
    print("hist для нескольких столбцов рисуется наложением (DataFrame.plot.hist)")
except Exception as e:
    print(type(e).__name__)
plt.close("all")
# barh удобнее bar при длинных названиях (подписи горизонтальные, не надо наклонять). bins - число интервалов гистограммы:
# мало -> грубо, много -> шумно. alpha - прозрачность: при наложении нескольких рядов видно перекрытие. Без figsize
# используется rcParams["figure.figsize"] (6.4x4.8). legend=True/False/'reverse' управляет легендой. Series.plot.hist строит
# распределение ОДНОЙ переменной; DataFrame.plot.hist рисует по гистограмме на каждый столбец (наложение), а не совместное распределение.

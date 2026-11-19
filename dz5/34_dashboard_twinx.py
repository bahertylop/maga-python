"""
Задача 34 (операционный дашборд: twinx + mdates + Formatter).
Показать выручку линией, число машин столбцами на правой оси,
30-дневное скользящее среднее и общую легенду.

Объяснения:
- rolling(30).mean() сглаживает дневные колебания и показывает тренд примерно за месяц.
- twinx создаёт вторую ось Y; иначе масштабы денег и количества мешают друг другу.
- Цвета #1f77b4 и #ff7f0e достаточно контрастны; цвета не единственный способ различения.
- alpha=0.2 делает столбцы прозрачными, width=0.8 оставляет промежутки.
- Для web обычно достаточно dpi=150, для печати лучше dpi=300.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

rng = np.random.default_rng(34)
dates = pd.date_range("2025-01-01", periods=180, freq="D")
cars = rng.integers(15, 45, len(dates))
revenue = cars * rng.uniform(1.4e6, 2.1e6, len(dates))
df = pd.DataFrame({"date": dates, "cars": cars, "revenue": revenue})

fig, ax1 = plt.subplots(figsize=(12, 6), layout="constrained")
ax2 = ax1.twinx()
l1, = ax1.plot(df.date, df.revenue, color="#1f77b4", label="Выручка", linewidth=2)
l2, = ax1.plot(df.date, df.revenue.rolling(30).mean(), color="#2ca02c",
               linestyle="--", label="SMA 30")
bars = ax2.bar(df.date, df.cars, color="#ff7f0e", alpha=0.2, width=0.8, label="Автомобили")
ax1.xaxis.set_major_locator(mdates.MonthLocator())
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax1.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v/1e6:.1f}M ₽"))
ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:.0f}"))
ax1.set_ylabel("Выручка")
ax2.set_ylabel("Продано автомобилей")
ax1.set_title("Операционный дашборд автосалона")
plt.setp(ax1.get_xticklabels(), rotation=40, ha="right")
ax1.legend([l1, l2, bars], ["Выручка", "SMA 30", "Автомобили"], loc="upper left")
fig.savefig("dashboard_web.png", dpi=150)
fig.savefig("dashboard_print.png", dpi=300)
plt.show()

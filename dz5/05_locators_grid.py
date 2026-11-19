"""Задача 5. Локаторы, формат даты и двухуровневая сетка."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
if Path("sales.csv").exists():
    df = pd.read_csv("sales.csv", parse_dates=["date"])
    x = df["date"]
    y = df["revenue"] if "revenue" in df else df.iloc[:, -1]
else:
    x = pd.date_range("2026-01-01", periods=90, freq="D")
    y = [900_000 + (i % 15) * 120_000 for i in range(90)]
fig, ax = plt.subplots(layout="constrained")
ax.plot(x, y)
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.yaxis.set_major_locator(mticker.MultipleLocator(1_000_000))
ax.yaxis.set_minor_locator(mticker.AutoMinorLocator())
ax.grid(which="major", linestyle="--", alpha=.5)
ax.grid(which="minor", linestyle=":", alpha=.3)
ax.tick_params(which="minor", length=0)
# Locator выбирает позиции tick, Formatter определяет подписи к этим позициям — разделение ролей.
# AutoMinorLocator делит промежутки между major ticks на меньшие деления автоматически.
# MultipleLocator(1_000_000) делает понятные круглые шаги денежной оси.
# ax.set_xlim(5,-5) инвертирует ось; может быть полезно для обратного порядка.
# tick_params(length=0) скрывает маленькие штрихи minor ticks, сетка остаётся.
# set_xlim за пределами данных не обрезает данные физически — показывает пустые поля;
# если диапазон не пересекается с данными, область графика будет пустой.
plt.show()

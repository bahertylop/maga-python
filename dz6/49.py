r"""
**Задача 49 (Matplotlib: subplots, стили, даты).** Создайте `fig, axes = plt.subplots(2, 2, figsize=(14, 10), layout="constrained")`. На каждом подграфике постройте свой тип через `df.plot(ax=axes[i, j])`. Примените `ax.set_title()`, `ax.set_xlabel()`, `ax.grid()`, `ax.axhline()`, `ax.annotate()`. Используйте `plt.style.use("seaborn-v0_8")`. Настройте `mdates.MonthLocator(interval=3)` и `DateFormatter("%b %Y")`. Сохраните через `fig.savefig("plot.png", dpi=300, bbox_inches="tight")`. Ожидаемый вывод: 2×2 сетка подграфиков; стиль `seaborn-v0_8`; даты на оси X в формате `"Jan 2024"`. В комментариях объясните: когда нужен Matplotlib вместо `df.plot` (тонкая настройка); как `layout="constrained"` убирает обрезку; зачем `dpi=300` (качество печати); как `ax.annotate` работает с `xytext` (смещение текста); что произойдёт при сохранении без `bbox_inches="tight"` (обрезанные подписи); как комбинировать `df.plot` и Seaborn на одной фигуре.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

plt.style.use("seaborn-v0_8")
rng = np.random.default_rng(49)
idx = pd.date_range("2024-01-01", periods=24, freq="MS")
df = pd.DataFrame({"Toyota": rng.integers(50, 120, 24), "BMW": rng.integers(30, 90, 24), "Kia": rng.integers(40, 100, 24)}, index=idx)
fig, axes = plt.subplots(2, 2, figsize=(14, 10), layout="constrained")
df.plot(ax=axes[0, 0], title="line"); df.set_axis(df.index.strftime("%b %y")).plot(kind="bar", ax=axes[0, 1], title="bar", legend=False, width=0.8)
df.plot(kind="area", ax=axes[1, 0], title="area", alpha=0.6); df["Toyota"].plot(kind="hist", ax=axes[1, 1], bins=8, title="hist")
for ax in axes.flat:
    ax.set_xlabel("Месяц" if ax is not axes[1, 1] else "Продажи"); ax.grid(True, alpha=0.4)
mean = df["Toyota"].mean(); axes[0, 0].axhline(mean, color="red", ls="--", lw=1)
peak = df["Toyota"].idxmax()
axes[0, 0].annotate("пик Toyota", xy=(peak, df["Toyota"].max()), xytext=(peak, df["Toyota"].max() + 25), arrowprops=dict(arrowstyle="->"))
axes[0, 0].xaxis.set_major_locator(mdates.MonthLocator(interval=3)); axes[0, 0].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
axes[1, 0].xaxis.set_major_locator(mdates.MonthLocator(interval=3)); axes[1, 0].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
out = Path(__file__).parent / "plot_49.png"
fig.savefig(out, dpi=300, bbox_inches="tight"); print("сохранено:", out.name, out.stat().st_size // 1024, "КБ"); plt.close(fig)
# Matplotlib нужен, когда df.plot не хватает: линии-ориентиры (axhline), аннотации, форматирование дат, несколько осей.
# layout="constrained" сам подбирает отступы, чтобы подписи не налезали и не обрезались. dpi=300 - печатное качество (мелкие
# детали и шрифты остаются чёткими). annotate: xy - ТОЧКА, на которую указываем, xytext - позиция ТЕКСТА (смещение от точки),
# arrowprops рисует стрелку между ними. Без bbox_inches="tight" подписи/легенда за пределами осей могут быть обрезаны.
# df.plot и Seaborn комбинируются через общий ax: sns.lineplot(..., ax=axes[i, j]) и df.plot(ax=axes[k, l]) на одной фигуре.
# Замечание: у bar ось категориальная (позиции 0..N), поэтому подписи месяцев заданы строками (strftime), а mdates-форматтер применён только к line/area.

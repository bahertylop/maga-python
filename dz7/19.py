"""
Задача 19 (stackplot и fill_between для диапазонов). Автосалон показывает структуру выручки по каналам (салон, онлайн, партнёры) и отдельно — доверительный интервал для прогноза продаж через салон. Постройте ax.stackplot(dates, salon, online, partners, labels=["Салон", "Онлайн", "Партнёры"], alpha=0.8) — суммируемые данные. Для доверительного интервала прогноза постройте lo = forecast.rolling(7).quantile(0.1); hi = forecast.rolling(7).quantile(0.9); ax.fill_between(dates, lo, hi, alpha=0.2, color="steelblue"). Ожидаемый вывод: накопленные области и CI-полоса на второй оси или на отдельном графике. В комментариях объясните: когда stackplot (суммируемые данные), когда fill_between (диапазоны — CI, оптимистичный/пессимистичный прогноз); что делает baseline="sym" (симметрично относительно нуля — полезно для знакопеременных данных типа прибыли/убытка); как where= закрашивает только часть (fill_between(..., where=(y > threshold))); что произойдёт с stackplot при 8+ категориях и как объединить мелкие; как stackplot связан с накопленным bar(bottom=...) и когда что использовать; как аннотировать проценты подписей внутри каждой области.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
rng = np.random.default_rng(19)

dates = pd.date_range("2024-01-01", periods=120, freq="D")
t = np.arange(120)
salon = 60 + 0.2 * t + rng.normal(0, 4, 120)
online = 25 + 0.3 * t + rng.normal(0, 3, 120)
partners = 15 + 0.05 * t + rng.normal(0, 2, 120)
forecast = pd.Series(salon + rng.normal(0, 8, 120), index=dates)   # шумный прогноз по салону

fig, axes = plt.subplots(3, 1, figsize=(12, 13), layout="constrained")

# --- 1. stackplot: СУММИРУЕМЫЕ части целого (выручка по каналам). Высота = сумма. ---
ax = axes[0]
polys = ax.stackplot(dates, salon, online, partners,
                     labels=["Салон", "Онлайн", "Партнёры"], alpha=0.8)
ax.legend(loc="upper left")
ax.set_title("stackplot: структура выручки по каналам")

# Проценты внутри областей: считаем долю каналов в выбранный момент и ставим текст
# в середину каждой полосы (нижняя граница + половина высоты).
k = 100
vals = np.array([salon[k], online[k], partners[k]])
cum = np.cumsum(vals) - vals / 2
for v, y in zip(vals, cum):
    ax.text(dates[k], y, f"{v / vals.sum():.0%}", ha="center", va="center",
            color="white", fontweight="bold")

# --- 2. fill_between: ДИАПАЗОН (CI, оптимистичный/пессимистичный сценарий) ---
# Это не слагаемые, а нижняя и верхняя границы одной величины.
ax = axes[1]
lo = forecast.rolling(7).quantile(0.1)
hi = forecast.rolling(7).quantile(0.9)
ax.plot(dates, forecast.rolling(7).mean(), color="steelblue", label="Прогноз (скользящее среднее)")
ax.fill_between(dates, lo, hi, alpha=0.2, color="steelblue", label="Диапазон 10-90%")
# where= закрашивает только часть, где условие истинно (здесь - где верхняя граница выше порога)
threshold = 85
ax.fill_between(dates, lo, hi, where=(hi > threshold), alpha=0.4, color="green",
                label=f"Верх > {threshold}")
ax.axhline(threshold, color="gray", ls="--")
ax.legend(loc="upper left")
ax.set_title("fill_between: доверительный интервал прогноза по салону")

# --- 3. baseline="sym" - «потоковый» график, симметричный относительно нуля ---
# По умолчанию baseline="zero" (слои растут от нуля). "sym" центрирует стопку вокруг 0:
# удобно для знакопеременных данных (прибыль/убыток) и для streamgraph; "wiggle" минимизирует
# изменения наклона слоёв.
ax = axes[2]
ax.stackplot(dates, salon, online, partners, baseline="sym",
             labels=["Салон", "Онлайн", "Партнёры"], alpha=0.8)
ax.legend(loc="upper left")
ax.set_title('stackplot(baseline="sym")')

# Много категорий (8+): цвета повторяются/сливаются, нижние слои «давят» наверх,
# а малые слои невидимы. Решение - объединить мелкие в «Прочее»:
#   big = df.sum().nlargest(5).index; df["Прочее"] = df.drop(columns=big).sum(axis=1)
# stackplot vs bar(bottom=...): stackplot - непрерывные области для временных рядов
# (значения на оси X соединены), bar(bottom=...) - дискретные категории (марки, месяцы),
# позволяет планки ошибок и подписи над каждым столбцом.
for a in axes:
    a.grid(alpha=0.3)
fig.savefig(HERE / "task_19.png", dpi=150)
plt.show()

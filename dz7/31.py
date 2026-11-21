"""
Задача 31 (errorbar + fill_between для CI + resample). Автосалон мониторит недельные продажи с доверительным интервалом. Сгруппируйте по неделям: weekly = measurements.resample("W", on="date")["cars_sold"].agg(["mean", "std", "count"]). Вычислите sem = weekly["std"] / np.sqrt(weekly["count"]), ci = 1.96 * sem (95% CI для нормального распределения). Постройте ax.errorbar(weekly.index, weekly["mean"], yerr=ci, fmt="o-", capsize=6, color="steelblue") и ax.fill_between(weekly.index, weekly["mean"] - ci, weekly["mean"] + ci, alpha=0.15, color="steelblue"). Ожидаемый вывод: среднее с планками ошибок и той же полосой CI. В комментариях объясните: чем SD отличается от SEM (первое — разброс наблюдений, второе — точность оценки среднего; SEM всегда меньше SD при n > 1); зачем 1.96 * sem (95% CI для нормального распределения); когда fill_between читается лучше errorbar (плотные ряды — планки сливаются в «частокол»); как resample("W") группирует по неделям и почему нужен DatetimeIndex; что произойдёт при count = 1 в неделе (sem = 0/1 = 0, CI сжимается до точки); как использовать t-распределение для малых выборок (scipy.stats.t.ppf(0.975, df=count-1) вместо 1.96).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import t

HERE = Path(__file__).parent
rng = np.random.default_rng(31)

dates = pd.date_range("2024-01-01", "2024-03-31", freq="D")
measurements = pd.DataFrame({"date": dates,
                             "cars_sold": 45 + 0.1 * np.arange(len(dates)) + rng.normal(0, 8, len(dates))})
measurements = measurements.iloc[:-6]   # последняя неделя неполная (всего 1 день) - для демонстрации count=1

# resample("W") - группировка по календарным неделям (по умолчанию неделя заканчивается в
# воскресенье). Работает по ВРЕМЕННОМУ индексу: либо DatetimeIndex, либо колонка
# через on="date" (колонка должна быть datetime). Без времени resample не знает, к какой
# неделе относить строку.
weekly = measurements.resample("W", on="date")["cars_sold"].agg(["mean", "std", "count"])

# SD - разброс отдельных наблюдений; SEM = SD / sqrt(n) - точность оценки СРЕДНЕГО
# (чем больше n, тем уже). При n>1 SEM < SD. Доверительный интервал строят по SEM.
# 1.96 - 97.5-й процентиль нормального распределения: mean ± 1.96*SEM = 95% CI.
sem = weekly["std"] / np.sqrt(weekly["count"])
ci = 1.96 * sem

# Для малых выборок нормальное приближение занижает интервал - берём t-распределение с
# df = n-1 (при n -> ∞ t.ppf -> 1.96). При count=1: pandas считает std по n-1 -> NaN
# (деление на 0), а не 0; поэтому CI для такой недели не определён (планки/полоса не
# рисуются) - честнее, чем «точка с нулевой погрешностью». Если подставить std=0 вручную,
# интервал схлопнется в точку, создавая ложное впечатление точности.
ci_t = t.ppf(0.975, df=weekly["count"] - 1) * sem

fig, axes = plt.subplots(1, 2, figsize=(15, 6), layout="constrained", sharey=True)

ax = axes[0]
ax.errorbar(weekly.index, weekly["mean"], yerr=ci, fmt="o-", capsize=6, color="steelblue")
ax.fill_between(weekly.index, weekly["mean"] - ci, weekly["mean"] + ci, alpha=0.15, color="steelblue")
ax.set_title("95% CI (1.96·SEM): errorbar + fill_between")

# fill_between лучше errorbar на плотных рядах (сотни точек): планки сливаются в «частокол»,
# а полоса остаётся чистой. errorbar лучше при немногих точках: показывает конкретные значения.
ax = axes[1]
ax.plot(weekly.index, weekly["mean"], "o-", color="steelblue", label="Среднее")
ax.fill_between(weekly.index, weekly["mean"] - ci, weekly["mean"] + ci, alpha=0.15,
                color="steelblue", label="CI (нормальное)")
ax.fill_between(weekly.index, weekly["mean"] - ci_t, weekly["mean"] + ci_t, alpha=0.15,
                color="orange", label="CI (t-распределение)")
ax.legend()
ax.set_title("Нормальное vs t")

for a in axes:
    a.set_ylabel("Продажи, шт./день")
    a.grid(alpha=0.3)
    a.tick_params(axis="x", rotation=30)
print(weekly.tail(3))
fig.savefig(HERE / "task_31.png", dpi=150)
plt.show()

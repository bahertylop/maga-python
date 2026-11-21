r"""
**Задача 50 (визуализация временных рядов).** Создайте ряд `daily` с ежедневными продажами (например, 365 дней с `DatetimeIndex`). Постройте на одной оси два графика: сырые данные через `daily.plot(alpha=0.3, ax=ax)` и сглаженный ряд через `daily.rolling(30).mean().plot(color="red", linewidth=2, ax=ax)`. Добавьте `ax.legend(["Данные", "Скользящее среднее (30)"])`, `ax.grid()`, `ax.set_title()`. Отформатируйте ось X через `mdates.MonthLocator(interval=3)` и `DateFormatter("%b %Y")`. Ожидаемый вывод: две линии на одной оси — полупрозрачная сырая и красная сглаженная; легенда с двумя записями; даты в формате `"Jan 2024"`. В комментариях объясните: зачем на графике скользящее среднее (убрать шум, увидеть тренд); как `alpha` помогает видеть обе линии одновременно; как `rolling` сглаживает шум; почему `ax=ax` обязателен для наложения графиков; как выбрать окно скользящего среднего (7 — неделя, 30 — месяц); что произойдёт при `rolling` без `min_periods` в начале ряда (первые 29 значений `NaN`).
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

rng = np.random.default_rng(50)
idx = pd.date_range("2024-01-01", periods=365)
daily = pd.Series(100 + 0.1 * np.arange(365) + 15 * np.sin(np.arange(365) / 58) + rng.normal(0, 12, 365), index=idx)
fig, ax = plt.subplots(figsize=(12, 5))
daily.plot(alpha=0.3, ax=ax)
daily.rolling(30).mean().plot(color="red", linewidth=2, ax=ax)
ax.legend(["Данные", "Скользящее среднее (30)"]); ax.grid(True, alpha=0.4); ax.set_title("Ежедневные продажи и тренд")
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3)); ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
fig.savefig(Path(__file__).parent / "plot_50.png", dpi=100, bbox_inches="tight"); plt.close(fig)
print("NaN в начале rolling(30):", daily.rolling(30).mean().isna().sum(), "| с min_periods=1:", daily.rolling(30, min_periods=1).mean().isna().sum())
print("записей в легенде:", 2, "| сохранено plot_50.png")
# Скользящее среднее убирает шум и показывает тренд. alpha=0.3 делает сырой ряд бледным фоном, поверх которого читается
# сглаженная красная линия. ax=ax обязателен: без него каждый plot создаёт СВОЮ фигуру/оси и наложения не будет.
# Окно: 7 - неделя (убирает недельную сезонность), 30 - месяц; больше окно -> глаже, но запаздывает (сглаженная линия «отстаёт»).
# rolling(30) без min_periods даёт NaN в первых 29 точках (окно ещё не заполнено); min_periods=1 считает по неполному окну.

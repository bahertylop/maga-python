"""
Задача 33 (форматирование дат через mdates).
Автосалон готовит график сезонности продаж за 3 года.
Сравнить: MonthLocator(interval=3)+DateFormatter; AutoDateLocator+AutoDateFormatter;
WeekdayLocator по понедельникам. Метки повернуть на 45 градусов.

Объяснения:
- Locator определяет места делений, Formatter — текст этих делений.
- parse_dates нужен, чтобы даты были datetime, а не строками.
- %b — короткое имя месяца (Jan), %B — полное (January).
- AutoDateLocator удобен как автоматический выбор частоты.
- MonthLocator(interval=12) оставит всего около 3 делений за 3 года.
- YearLocator(base=5) пригоден для очень длинных рядов.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

rng = np.random.default_rng(33)
dates = pd.date_range("2023-01-01", periods=1095, freq="D")
sales = 25 + 8*np.sin(np.arange(len(dates))*2*np.pi/365) + rng.normal(0, 3, len(dates))
df = pd.DataFrame({"date": dates, "cars_sold": np.maximum(0, sales)})

fig, axes = plt.subplots(3, 1, figsize=(12, 10), layout="constrained")
# (а) Деления раз в 3 месяца.
axes[0].plot(df.date, df.cars_sold)
axes[0].xaxis.set_major_locator(mdates.MonthLocator(interval=3))
axes[0].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
axes[0].set_title("MonthLocator: каждые 3 месяца")

# (б) Matplotlib сам выбирает частоту делений.
axes[1].plot(df.date, df.cars_sold)
loc = mdates.AutoDateLocator()
axes[1].xaxis.set_major_locator(loc)
axes[1].xaxis.set_major_formatter(mdates.AutoDateFormatter(loc))
axes[1].set_title("AutoDateLocator / AutoDateFormatter")

# (в) Только понедельники.
axes[2].plot(df.date, df.cars_sold)
axes[2].xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%d.%m (%a)"))
axes[2].set_title("WeekdayLocator: понедельники")
for ax in axes:
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    ax.set_ylabel("Продажи")
plt.show()

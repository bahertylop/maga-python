"""Задача 3. Кастомный форматтер для цены в рублях."""
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

class PriceFormatter(mticker.Formatter):
    def __call__(self, x, pos=None):
        return f"{x:,.0f} ₽".replace(",", " ")  # 2 500 000 ₽
months = pd.date_range("2026-01-01", periods=6, freq="MS")
prices = [1_850_000, 1_920_000, 2_050_000, 2_100_000, 2_240_000, 2_300_000]
fig, ax = plt.subplots(layout="constrained")
ax.plot(months, prices, marker="o")
ax.yaxis.set_major_formatter(PriceFormatter())
ax.set_xlabel("Месяц", labelpad=15)
ax.set_ylabel("Средняя цена")
ax.set_title("Средняя цена автомобиля по месяцам", fontweight="bold", fontfamily="serif", loc="left")
# Formatter — объект в системе ticker Matplotlib; можно хранить состояние (валюту, суффикс).
# Наследование Formatter даёт объектный интерфейс/настройки; FuncFormatter удобен для простой функции.
# serif — семейство, конкретный шрифт может отличаться ОС; для точных отчётов задавайте доступный шрифт.
# labelpad — расстояние подписи оси от оси; его увеличивают при тесном макете.
# loc='left' прижимает заголовок к левому краю Axes. fontdict удобен для общего словаря настроек.
# Пример fontdict: text_style={'fontweight':'bold','fontfamily':'serif'}; применяйте к нескольким текстам.
plt.show()

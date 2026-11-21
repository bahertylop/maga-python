"""
Задача 32 (форматирование чисел: собственные Formatter-классы). Автосалон готовит финансовый отчёт: выручка доходит до 100 млн руб., конверсия измеряется в процентах, а продажи — в тысячах автомобилей. Стандартные форматтеры выглядят «сыро». Реализуйте три класса: class CompactFormatter(mticker.Formatter) (1500000 → "1.5M", 250000 → "250K"), class RubleFormatter (1500000 → "1 500 000 ₽" через f"{x:,.0f} ₽"), class PercentFormatterCustom (0.15 → "15.0%"). Сравните с готовыми EngFormatter(unit="₽") и PercentFormatter(1.0). Примените к трём подграфикам. Ожидаемый вывод: разные форматы на одной и той же оси Y. В комментариях объясните: зачем ООП-класс вместо FuncFormatter; как Formatter встраивается в Locator и почему это разделение ответственности; почему PercentFormatter(1.0) ожидает доли (0.25 → 25%), а не проценты (что было бы при PercentFormatter(100)); когда StrMethodFormatter("{x:.2f}") проще класса; как EngFormatter использует инженерные приставки (k, M, G) и когда это удобнее «M/K»; как сохранить единый формат в отчёте через plt.rcParams (нет стандартного параметра — нужна своя функция-обёртка).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

HERE = Path(__file__).parent


# Класс вместо FuncFormatter: можно хранить состояние и настройки (число знаков, единицу,
# разделитель), переиспользовать и наследовать, тестировать отдельно, давать имя в
# коде отчёта. FuncFormatter - просто обёртка над функцией, удобна для разовых случаев.
# Разделение ответственности: Locator решает ГДЕ ставить деления (0, 25M, 50M...), Formatter -
# КАК подписать значение. Ось вызывает formatter(x, pos) для каждого деления от locator.
class CompactFormatter(mticker.Formatter):
    def __init__(self, decimals=1):
        self.decimals = decimals

    def __call__(self, x, pos=None):
        for limit, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
            if abs(x) >= limit:
                v = x / limit
                s = f"{v:.{self.decimals}f}".rstrip("0").rstrip(".")   # 1.0M -> 1M, 1.5M -> 1.5M
                return f"{s}{suffix}"
        return f"{x:.0f}"


class RubleFormatter(mticker.Formatter):
    def __call__(self, x, pos=None):
        # f"{x:,.0f}" даёт запятые как разделитель тысяч, меняем на пробел
        return f"{x:,.0f} ₽".replace(",", " ")


class PercentFormatterCustom(mticker.Formatter):
    def __init__(self, decimals=1):
        self.decimals = decimals

    def __call__(self, x, pos=None):
        return f"{x * 100:.{self.decimals}f}%"      # доля 0.15 -> "15.0%"


def apply_report_format(ax, kind):
    """Единый стиль отчёта. В rcParams нет параметра для форматтера оси, поэтому делаем
    свою функцию-обёртку и вызываем её для каждой оси (или в классе-билдере)."""
    fmt = {"money": RubleFormatter(), "compact": CompactFormatter(),
           "percent": PercentFormatterCustom()}[kind]
    ax.yaxis.set_major_formatter(fmt)
    ax.grid(alpha=0.3)


rng = np.random.default_rng(32)
months = np.arange(1, 13)
revenue = np.cumsum(rng.uniform(2e6, 1e7, 12))            # до ~100 млн
conversion = rng.uniform(0.05, 0.25, 12)                  # ДОЛИ (0.15 = 15%)
sales_k = rng.uniform(5, 40, 12)                          # тысячи автомобилей

fig, axes = plt.subplots(2, 3, figsize=(17, 9), layout="constrained")

# Верхний ряд: собственные классы
axes[0, 0].plot(months, revenue, marker="o")
axes[0, 0].yaxis.set_major_formatter(CompactFormatter())
axes[0, 0].set_title("CompactFormatter: 1.5M, 250K")

axes[0, 1].plot(months, revenue, marker="o")
axes[0, 1].yaxis.set_major_formatter(RubleFormatter())
axes[0, 1].set_title("RubleFormatter: 1 500 000 ₽")

axes[0, 2].plot(months, conversion, marker="o")
axes[0, 2].yaxis.set_major_formatter(PercentFormatterCustom())
axes[0, 2].set_title("PercentFormatterCustom: 15.0%")

# Нижний ряд: готовые форматтеры
# EngFormatter: инженерные приставки СИ (k, M, G...) со степенями тройками 10^3; «M» тут - мега.
# Удобно для физических/технических величин с единицами (Гц, В, ₽) и когда нужны
# стандартные приставки; CompactFormatter гибче по виду (K/M/B, без пробела), но это ручная работа.
axes[1, 0].plot(months, revenue, marker="o")
axes[1, 0].yaxis.set_major_formatter(mticker.EngFormatter(unit="₽"))
axes[1, 0].set_title("EngFormatter(unit='₽')")

# StrMethodFormatter("{x:.2f}") проще класса, когда нужна ОДНА строка формата без логики:
# "{x:.0f}K", "{x:.2f}", "{x:,.0f}". Класс - когда нужна логика (ветвления, K/M/B).
axes[1, 1].plot(months, sales_k, marker="o")
axes[1, 1].yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.0f}K"))
axes[1, 1].set_title("StrMethodFormatter('{x:.0f}K')")

# PercentFormatter(xmax=1.0): xmax - значение, которое соответствует 100%. Для долей
# (0.25 = 25%) xmax=1.0 -> 0.25 станет «25%». PercentFormatter(100) ждёт, что данные
# уже в процентах (25 -> 25%); на данных-долях он показал бы 0.25 -> «0.25%» - ошибка
# в 100 раз, частая ловушка.
axes[1, 2].plot(months, conversion, marker="o")
axes[1, 2].yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
axes[1, 2].set_title("PercentFormatter(1.0)")

for a in axes.ravel():
    a.set_xlabel("Месяц")
    a.grid(alpha=0.3)
fig.savefig(HERE / "task_32.png", dpi=150)

# Проверка единого формата через обёртку
fig2, ax = plt.subplots(figsize=(8, 5), layout="constrained")
ax.plot(months, revenue)
apply_report_format(ax, "compact")
plt.show()

"""
Задача 21 (twinx на данных автосалона). Автосалон визуализирует число проданных автомобилей и средний чек — две переменные с разными масштабами (штуки 10–100, средний чек 1–5 млн руб.). Постройте число автомобилей на ax1 столбцами и средний чек на ax2 = ax1.twinx() линией. Обязательно свяжите цвета: ax1.tick_params(axis="y", labelcolor="C0"), ax2.tick_params(axis="y", labelcolor="C1"). Настройте FuncFormatter для среднего чека (f"{v/1e6:.1f}M ₽") и автомобилей (f"{v:.0f}"). Соберите общую легенду через get_legend_handles_labels(). Ожидаемый вывод: число автомобилей и средний чек на одной оси с разными шкалами; цвета осей совпадают с цветом данных. В комментариях объясните: зачем twinx (несопоставимые масштабы — без него средний чек «схлопнется» в плоскую линию на фоне числа автомобилей); почему обязательно связывать цвет данных и осей; как get_legend_handles_labels() собирает элементы с обеих осей и почему ax1.legend() покажет только линии ax1; когда twiny (вторая ось X) уместнее — например, две шкалы по датам (дни и недели); как ax2.spines["right"].set_color("C1") красит правую рамку в цвет данных; что произойдёт без set_ylim на каждой оси — Matplotlib сам подберёт диапазон, но иногда начнёт с нуля и «сплющит» средний чек (2.5M и 3.0M будут неразличимы).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

HERE = Path(__file__).parent
rng = np.random.default_rng(21)

months = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
cars = rng.integers(20, 95, 12)
avg_check = 2.5e6 + 0.5e6 * np.sin(np.linspace(0, 3, 12)) + rng.normal(0, 8e4, 12)

fig, ax1 = plt.subplots(figsize=(12, 6), layout="constrained")

# Столбцы - число автомобилей (левая ось, цвет C0)
ax1.bar(months, cars, color="C0", alpha=0.75, label="Продано, шт.")

# twinx() создаёт ВТОРУЮ ось Y с общей осью X. Без неё средний чек (миллионы) и штуки
# (десятки) жили бы на одной шкале 0..5 000 000, и линия штук «схлопнулась» бы в ноль
# (или наоборот чек стал бы плоской линией).
ax2 = ax1.twinx()
ax2.plot(months, avg_check, color="C1", marker="o", lw=2.5, label="Средний чек, ₽")

# Цвета осей = цвета данных: при двух осях читатель иначе не поймёт, к какой оси относится
# линия/столбцы (ошибки в интерпретации - частая проблема двойных осей).
ax1.tick_params(axis="y", labelcolor="C0")
ax2.tick_params(axis="y", labelcolor="C1")
ax1.set_ylabel("Продано, шт.", color="C0")
ax2.set_ylabel("Средний чек", color="C1")
ax2.spines["right"].set_color("C1")      # правая рамка в цвет данных ax2
ax1.spines["left"].set_color("C0")

ax1.yaxis.set_major_formatter(FuncFormatter(lambda v, pos: f"{v:.0f}"))
ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, pos: f"{v / 1e6:.1f}M ₽"))

# Явные пределы. Без set_ylim Matplotlib подбирает их сам: у столбцов ось всегда
# включает 0 (так задано для bar), а для линии может начаться от 0 (если ядро в
# автомасштабе включает 0 из-за margins/sticky edges) - и разница 2.5M и 3.0M
# «сплющится». Явный диапазон растягивает нужную часть шкалы.
ax1.set_ylim(0, 110)
ax2.set_ylim(avg_check.min() * 0.9, avg_check.max() * 1.1)

# Общая легенда: каждая ось хранит СВОИ элементы. ax1.legend() покажет только то, что нарисовано
# на ax1 (столбцы), линия ax2 в неё не попадёт. get_legend_handles_labels() возвращает
# (handles, labels) для оси: склеиваем списки обеих осей и создаём одну легенду.
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper left")

# twiny() уместен, когда нужна ВТОРАЯ ШКАЛА ПО X для тех же данных: например, дни (снизу) и
# недели (сверху), °C/°F, метры/футы; twinx - когда разные величины по Y при одном X.
ax1.set_title("Продажи и средний чек (twinx)")
ax1.grid(axis="y", alpha=0.3)
fig.savefig(HERE / "task_21.png", dpi=150)
plt.show()

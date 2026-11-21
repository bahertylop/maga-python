"""
Задача 14 (продвинутая легенда из groupby). Автосалон имеет 8 марок и хочет показать на графике только 2 ключевых (например, «Toyota» и «Hyundai»), но остальные оставить построенными — чтобы видеть общий фон. Загрузите sales_by_brand.csv, постройте линии циклом for brand, g in df.groupby("brand"): line, = ax.plot(...); lines[brand] = line. Создайте две легенды: выборочную через ax.legend(handles=[lines["Toyota"], lines["Hyundai"]], loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0) — вынесенную за график, и полную через ncol=2 внутри. Ожидаемый вывод: две легенды — выборочная вне графика и полная внутри. В комментариях объясните: зачем запятая в line, = ax.plot(...) (распаковка кортежа из одного элемента); что произойдёт без запятой и почему handles=[line] не сработает (AttributeError: 'tuple' object has no attribute 'set_label'); как bbox_to_anchor в долях осей задаёт точку привязки и почему loc="center left" + bbox_to_anchor=(1.02, 0.5) помещает легенду справа; что делает borderaxespad=0; почему при многих категориях полная легенда перегружает график и лучше использовать выборочную; как автоматически отсортировать категории через sorted(lines.items()), чтобы в легенде был алфавитный порядок.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
CSV = HERE / "sales_by_brand.csv"

if not CSV.exists():
    rng = np.random.default_rng(1)
    brands = ["Toyota", "Hyundai", "Kia", "Volkswagen", "Skoda", "Renault", "Lada", "Haval"]
    months = pd.date_range("2024-01-01", periods=12, freq="MS")
    rows = []
    for b in brands:
        level = rng.integers(40, 160)
        s = level + np.cumsum(rng.normal(0, 6, 12))
        rows += [(b, m, int(v)) for m, v in zip(months, s)]
    pd.DataFrame(rows, columns=["brand", "date", "count"]).to_csv(CSV, index=False)

df = pd.read_csv(CSV, parse_dates=["date"])

fig, ax = plt.subplots(figsize=(12, 6), layout="constrained")
KEY = ["Toyota", "Hyundai"]

lines = {}
for brand, g in df.groupby("brand"):
    # ax.plot ВСЕГДА возвращает СПИСОК Line2D (даже для одной линии), т.е. [Line2D].
    # `line, = ax.plot(...)` - распаковка списка из одного элемента: line станет самим
    # объектом Line2D. Без запятой line = [Line2D] (список): handles=[line] даст
    # вложенный список [[Line2D]], и legend упадёт с ошибкой вида
    # AttributeError: 'list'/'tuple' object has no attribute ... (у списка нет
    # методов Artist вроде set_label/get_label).
    line, = ax.plot(g["date"], g["count"], label=brand,
                    lw=2.8 if brand in KEY else 1.2,
                    alpha=1.0 if brand in KEY else 0.5)   # ключевые ярче - остальные «фон»
    lines[brand] = line

# Полная легенда ВНУТРИ графика: ncol=2 делает её компактнее. Эту легенду нужно
# зафиксировать через add_artist: следующий вызов ax.legend() заменит её на новую
# (у Axes только одна «штатная» легенда).
full = ax.legend(handles=[l for _, l in sorted(lines.items())],   # sorted(...) по имени марки ->
                 ncol=2, loc="upper left", fontsize=8,           # алфавитный порядок в легенде
                 title="Все марки")
ax.add_artist(full)

# Выборочная легенда СНАРУЖИ справа.
# bbox_to_anchor=(1.02, 0.5) - точка привязки в ДОЛЯХ ОСЕЙ (0..1): x=1.02 - чуть правее
# правого края, y=0.5 - середина по высоте. loc="center left" говорит, КАКОЙ точкой
# самой легенды (середина левого края) прикладываем к этой точке -> легенда стоит справа
# от графика и центрирована по вертикали.
# borderaxespad=0 - убирает отступ между легендой и точкой привязки (по умолчанию 0.5
# размера шрифта), иначе зазор будет больше 1.02.
ax.legend(handles=[lines[b] for b in KEY], loc="center left",
          bbox_to_anchor=(1.02, 0.5), borderaxespad=0, title="Ключевые")

# При 8+ категориях полная легенда занимает много места, перекрывает данные и цвета
# становятся неразличимыми - читатель ищет глазами нужный цвет. Выборочная легенда
# фокусирует внимание на главном, остальные остаются фоном.
ax.set(title="Продажи по маркам", xlabel="Месяц", ylabel="Продано, шт.")
ax.grid(alpha=0.3)
fig.savefig(HERE / "task_14.png", dpi=150, bbox_inches="tight")
plt.show()

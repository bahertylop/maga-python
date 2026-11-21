r"""
**Задача 19 (ffill/bfill/interpolate).** Создайте Series с пропусками (дневная выручка автосалона). Примените `ffill()`, `bfill()`, `ffill(limit=1)`. Создайте Series с `DatetimeIndex` и пропусками. Примените `interpolate(method="linear")`, `method="time"`, `method="polynomial", order=2`. Сравните результаты на неравномерном индексе. Примените `interpolate(limit_direction="both")`. Ожидаемый вывод: `ffill` копирует предыдущее значение, `bfill` — следующее; `linear` и `time` дают разные результаты на неравномерном индексе; `polynomial` может дать выбросы за пределы данных. В комментариях объясните: в каких случаях `time` лучше `linear` (когда интервалы между продажами неравномерны); почему `polynomial` может дать выбросы (феномен Рунге); как `limit_direction` влияет на заполнение с краёв (`"forward"`, `"backward"`, `"both"`); чем `ffill` отличается от `interpolate` по семантике (копирование vs аппроксимация); что произойдёт при `interpolate` на нечисловом столбце (`TypeError` или игнорирование); как `method="nearest"` работает на категориальных данных.
"""
import numpy as np
import pandas as pd

idx = pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-06", "2025-01-10"])
s = pd.Series([100.0, np.nan, 120.0, np.nan, 200.0], index=idx)
print("ffill:", s.ffill().tolist(), "| bfill:", s.bfill().tolist(), "| ffill(limit=1):", s.ffill(limit=1).tolist())
print("linear:", s.interpolate("linear").round(1).tolist())
print("time  :", s.interpolate("time").round(1).tolist(), "<- учитывает неравные интервалы дат")
print("poly2 :", s.interpolate("polynomial", order=2).round(1).tolist(), "(scipy; может «выстрелить»)")
edge = pd.Series([np.nan, 1.0, np.nan, 3.0, np.nan])
print("limit_direction both:", edge.interpolate(limit_direction="both").tolist())
print("nearest (краевые NaN остаются - экстраполяции нет):", edge.interpolate("nearest", limit_direction="both").tolist())
txt = pd.Series(["a", None, "c"])
try:
    print("interpolate на строках:", txt.interpolate().tolist())
except Exception as e:
    print("interpolate на str ->", type(e).__name__)
# time лучше linear, когда интервалы неравные (между продажами 1 день и 4 дня): linear считает точки равноудалёнными,
# time - пропорционально дате. polynomial может давать выбросы за пределами данных (феномен Рунге).
# limit_direction задаёт, с какой стороны заполнять края ("forward"/"backward"/"both"). ffill КОПИРУЕТ последнее значение,
# interpolate АППРОКСИМИРУЕТ между известными. nearest берёт ближайшее известное значение (годится для дискретных/кодированных данных).

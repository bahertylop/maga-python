"""
**Задача 21 (ось агрегации `axis`).** Дана матрица `sales` формы `(3, 4)`. Вычислите:
- `sales.sum()` — одно число;
- `sales.sum(axis=0)` — форма `(4,)`, сумма по месяцам;
- `sales.sum(axis=1)` — форма `(3,)`, сумма по маркам.

Повторите для `min`, `max`, `mean`, `std`. **Что продемонстрировать:** разницу `axis=0` и `axis=1`. **Вопросы:** почему `axis=0` «сворачивает» строки; как запомнить правило («`axis` — то, что исчезает»); что при `axis=2`; как сформулировать «средняя цена по маркам» через `axis`; как работает `axis=(0, 1)`.
"""
import numpy as np

sales = np.array([[120, 150, 90, 130], [110, 140, 100, 125], [130, 160, 95, 140]])
print("sum()       :", sales.sum())
print("sum(axis=0) :", sales.sum(axis=0), "- сумма по месяцам для каждой марки, shape", sales.sum(axis=0).shape)
print("sum(axis=1) :", sales.sum(axis=1), "- сумма по маркам для каждого месяца, shape", sales.sum(axis=1).shape)
for fn in ("min", "max", "mean", "std"):
    f = getattr(sales, fn)
    print(f"{fn:5s} all={f():.2f}  axis0={f(axis=0).round(2)}  axis1={f(axis=1).round(2)}")
# Правило: ось, ВДОЛЬ которой считаем, ИСЧЕЗАЕТ из shape. axis=0 «сворачивает строки»
# (идём сверху вниз по месяцам) -> остаётся (4,). axis=1 сворачивает столбцы -> (3,).
try:
    sales.sum(axis=2)
except Exception as e:
    print("axis=2 ->", type(e).__name__, e)
# «Средняя цена по маркам» при матрице (модели x марки) = mean(axis=0) (усредняем по моделям).
print("axis=(0, 1) = то же, что sum():", sales.sum(axis=(0, 1)))

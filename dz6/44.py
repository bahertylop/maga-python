r"""
**Задача 44 (broadcasting/axis/keepdims).** Создайте `sales` 3×4 (месяцы × категории автомобилей) и `offset = pd.Series([10, 20, 30, 40], index=sales.columns)`. Сложите `sales + offset`. Создайте `offset_col = pd.Series([5, 10, 15], index=sales.index)` — сложите через `sales.add(offset_col, axis=0)`. Попробуйте `sales + offset_col` без `axis`. Примените `sales.values - sales.values.mean(axis=1, keepdims=True)` и без `keepdims`. Ожидаемый вывод: `sales + offset` выравнивает по столбцам; `sales + offset_col` без `axis` даёт `NaN`; `keepdims=True` даёт форму `(3, 1)`, без — `(3,)` с ошибкой broadcasting. В комментариях объясните: почему `(3,)` несовместима с `(3, 4)` без `axis` (нужно выравнивание по строкам); как `fill_value` в `.add()` помогает; когда `keepdims` экономит код (сохранение размерности для broadcasting); что произойдёт при `axis=2` (`ValueError`); как `np.newaxis` заменяет `keepdims`; как broadcasting работает с трёхмерными массивами.
"""
import numpy as np
import pandas as pd

sales = pd.DataFrame(np.arange(12).reshape(3, 4), index=["янв", "фев", "мар"], columns=["седан", "SUV", "хэтч", "купе"])
offset = pd.Series([10, 20, 30, 40], index=sales.columns); print(sales + offset)
col = pd.Series([5, 10, 15], index=sales.index)
print(sales.add(col, axis=0))
print("sales + col без axis (выравнивание по столбцам -> NaN):\n", sales + col)
v = sales.to_numpy(float)
print("keepdims=True shape:", v.mean(axis=1, keepdims=True).shape, "| без:", v.mean(axis=1).shape)
print(v - v.mean(axis=1, keepdims=True))
try:
    v - v.mean(axis=1)
except ValueError as e:
    print("без keepdims ->", e)
print("newaxis эквивалент:", np.allclose(v - v.mean(axis=1)[:, np.newaxis], v - v.mean(axis=1, keepdims=True)))
partial = sales.iloc[:2, :2] * 100   # другой DataFrame: часть меток отсутствует
print("fill_value (между DataFrame; со Series не поддерживается):\n", sales.add(partial, fill_value=0))
try:
    sales.add(offset, axis=1, fill_value=0)
except NotImplementedError as e:
    print("fill_value со Series ->", e)
try:
    v.sum(axis=2)
except np.exceptions.AxisError as e:
    print("axis=2 ->", type(e).__name__, "-", e)
# Series + DataFrame выравнивает Series по СТОЛБЦАМ (по меткам), поэтому для вектора по строкам нужен .add(..., axis=0);
# без axis метки индекса «месяцев» ищутся среди столбцов -> всё NaN (union меток). (3,) не совместим с (3, 4): broadcasting
# выравнивает формы справа - (3,) считается строкой длины 3, а столбцов 4. keepdims=True сохраняет ось размером 1 -> (3, 1)
# и broadcasting работает; np.newaxis делает то же вручную. fill_value заменяет отсутствующую метку на значение до сложения.
# axis=2 для 2D-массива -> AxisError (подкласс ValueError и IndexError).

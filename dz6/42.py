r"""
**Задача 42 (unique/isin/set ops/duplicated).** Создайте два Series брендов. Примените `.unique()` и `np.unique()` — сравните сортировку. Примените `.value_counts()`, `.value_counts(normalize=True)`, `.value_counts(dropna=False)`. Используйте `np.intersect1d`, `np.union1d`, `np.setdiff1d`, `np.setxor1d`, `.isin()`. Примените `duplicated()`, `drop_duplicates()`. Ожидаемый вывод: `np.unique` сортирует, `.unique()` — нет (порядок появления); `value_counts(normalize=True)` возвращает доли; `setdiff1d` возвращает элементы первого массива, отсутствующие во втором. В комментариях объясните: почему `np.unique` сортирует (реализация через сортировку); когда `isin` удобнее `set` (векторизация, сохранение порядка); как `value_counts(dropna=False)` считает `NaN`; чем `drop_duplicates` отличается от `duplicated` (удаляет vs помечает); что произойдёт при `setxor1d` с одинаковыми массивами (пустой массив); как `value_counts` сортирует результат (по убыванию частоты).
"""
import numpy as np
import pandas as pd

a = pd.Series(["Toyota", "BMW", "Kia", "BMW", None, "Toyota"]); b = pd.Series(["Kia", "Audi", "BMW"])
print(".unique():", list(a.dropna().unique()), "(порядок появления) | np.unique:", list(np.unique(a.dropna().to_numpy())) , "(отсортирован)")
print(a.value_counts().to_dict(), "|", a.value_counts(normalize=True).round(2).to_dict(), "|", a.value_counts(dropna=False).to_dict())
x, y = a.dropna().to_numpy(), b.to_numpy()
print("intersect:", np.intersect1d(x, y), "| union:", np.union1d(x, y), "| setdiff:", np.setdiff1d(x, y), "| setxor:", np.setxor1d(x, y))
print("isin:", a.isin(b).tolist())
print("duplicated:", a.duplicated().tolist(), "| drop_duplicates:", a.drop_duplicates().tolist(), "| keep=False:", a.drop_duplicates(keep=False).tolist())
print("setxor1d одинаковых:", np.setxor1d(y, y))
# np.unique реализован через сортировку (находит соседние равные), поэтому возвращает отсортированный результат;
# Series.unique() - на хэш-таблице, порядок появления, быстрее и работает с NaN. isin удобнее set: векторизован, сохраняет порядок и
# длину Series (булева маска). value_counts(dropna=False) считает NaN отдельной строкой. duplicated только ПОМЕЧАЕТ повторы
# (булева маска), drop_duplicates УДАЛЯЕТ их. setxor1d одинаковых массивов - пустой массив (симметрическая разность).
# np.unique на object-массиве с None падает (None нельзя сравнивать со str) - поэтому выше сначала dropna().

"""
**Задача 22 (`keepdims` и broadcasting).** Дана `sales` формы `(3, 4)`. Вычислите среднее по строкам (по маркам внутри месяца):
- без `keepdims`: `row_means = sales.mean(axis=1)` — форма `(3,)`;
- с `keepdims=True`: `row_means_keep = sales.mean(axis=1, keepdims=True)` — форма `(3, 1)`.

Попробуйте вычесть `row_means` из `sales` — ошибка. Вычтите `row_means_keep` — работает. **Что продемонстрировать:** ошибку без `keepdims` и успех с ним. **Вопросы:** зачем `keepdims`; почему `(3,)` ≠ `(3, 1)` для broadcasting; когда `keepdims` экономит строку кода; как то же через `[:, np.newaxis]`; почему `keepdims` не меняет данные.
"""
import numpy as np

sales = np.array([[120, 150, 90, 130], [110, 140, 100, 125], [130, 160, 95, 140]], dtype=float)
row_means = sales.mean(axis=1)                       # (3,)
row_means_keep = sales.mean(axis=1, keepdims=True)   # (3, 1)
print(row_means.shape, row_means_keep.shape)
try:
    sales - row_means
except ValueError as e:
    print("без keepdims:", e)
print("с keepdims:\n", sales - row_means_keep)
# (3,) для broadcasting - это (1, 3): выравнивание идёт справа, 3 vs 4 - конфликт.
# (3, 1): ось длины 1 растягивается по 4 столбцам - каждая строка вычитает СВОЁ среднее.
# keepdims экономит строку reshape/np.newaxis; эквивалент: row_means[:, np.newaxis].
print("то же через newaxis:", np.allclose(sales - row_means[:, np.newaxis], sales - row_means_keep))
# keepdims не меняет значения, только форму результата (сохраняет свёрнутую ось как длины 1).

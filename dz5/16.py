"""
**Задача 16 (reshape).** Дан массив из 12 цен: `prices = np.arange(12) * 200000 + 500000`. Переформируйте:
- в `3×4` (`reshape(3, 4)`);
- в `2×6` (`reshape(2, 6)`);
- в `2×2×3` (`reshape(2, 2, 3)`);
- в `3×4` через `-1` (`reshape(3, -1)`).

Попробуйте `reshape(5, 5)` — ошибка. **Что продемонстрировать:** разные формы и `-1`. **Вопросы:** почему `reshape` не меняет данные; когда view, когда копия; зачем `-1`; как `reshape` связан с `order='C'` vs `order='F'`.
"""
import numpy as np

prices = np.arange(12) * 200000 + 500000
print("3x4 :\n", prices.reshape(3, 4))
print("2x6 :\n", prices.reshape(2, 6))
print("2x2x3 shape:", prices.reshape(2, 2, 3).shape)
print("reshape(3, -1) ->", prices.reshape(3, -1).shape, "(-1 NumPy вычислил сам: 12/3 = 4)")
try:
    prices.reshape(5, 5)
except ValueError as e:
    print("reshape(5,5) ->", e)
# reshape не меняет данные - только их ИНТЕРПРЕТАЦИЮ (shape/strides), поэтому обычно это
# view; копия создаётся, если новая форма несовместима с раскладкой в памяти
# (например, reshape транспонированного/нессмежного массива).
print("view:", prices.reshape(3, 4).base is prices)
a = np.arange(12).reshape(3, 4).T
print("reshape транспонированного - копия:", a.reshape(-1).base is None or a.reshape(-1).base is not a)
# order='C' (по строкам, по умолчанию) vs 'F' (по столбцам, как в Fortran): определяет, в
# каком порядке элементы раскладываются в новую форму.
print("order='C':\n", np.arange(6).reshape(2, 3), "\norder='F':\n", np.arange(6).reshape(2, 3, order="F"))

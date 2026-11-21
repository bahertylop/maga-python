"""
**Задача 18 (транспонирование и перестановка осей).** Дан массив `data` формы `(2, 3, 4)` — 2 филиала × 3 месяца × 4 марки. Получите:
- `data.T` — форма `(4, 3, 2)`;
- `np.transpose(data, (1, 0, 2))` — форма `(3, 2, 4)`;
- `np.swapaxes(data, 0, 2)` — форма `(4, 3, 2)`;
- `np.moveaxis(data, 0, -1)` — форма `(3, 4, 2)`.

Для `sales` формы `(3, 4)` сравните `sales.T` и `sales.transpose()`. **Что продемонстрировать:** все способы перестановки. **Вопросы:** почему транспонирование — view; как `moveaxis` отличается от `swapaxes`; когда транспонирование реально копирует.
"""
import numpy as np

data = np.arange(24).reshape(2, 3, 4)        # 2 филиала x 3 месяца x 4 марки
print("data.T                    :", data.T.shape)
print("transpose(data, (1,0,2))  :", np.transpose(data, (1, 0, 2)).shape)
print("swapaxes(data, 0, 2)      :", np.swapaxes(data, 0, 2).shape)
print("moveaxis(data, 0, -1)     :", np.moveaxis(data, 0, -1).shape)
sales = np.arange(12).reshape(3, 4)
print("sales.T == sales.transpose():", np.array_equal(sales.T, sales.transpose()), sales.T.shape)
# Транспонирование - view: меняются только shape и strides, данные не двигаются.
print("view:", data.T.base is data, "| shares_memory:", np.shares_memory(data, data.T))
# swapaxes меняет местами ДВЕ оси; moveaxis переносит ОДНУ ось на новое место, а остальные
# сохраняют относительный порядок (поэтому (2,3,4) -> (3,4,2), а не (4,3,2)).
# Реальная копия появляется, когда нужна непрерывная раскладка: np.ascontiguousarray(data.T),
# .T.reshape(...) для несовместимой формы, .copy(), .flatten().
print("contiguous?", data.T.flags["C_CONTIGUOUS"], "-> после ascontiguousarray:", np.ascontiguousarray(data.T).flags["C_CONTIGUOUS"])

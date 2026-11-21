"""
**Задача 28 (`searchsorted` и категоризация).** Границы ценовых категорий: `bounds = np.array([0, 1000000, 2000000, 3500000, 5000000, 50000000])`. Даны цены: `prices = np.array([700000, 1450000, 2200000, 3200000, 4100000, 6000000])`. Определите категорию:
- `np.searchsorted(bounds, prices)`;
- `np.searchsorted(bounds, prices, side='right')`.

Частоты: `np.bincount(np.searchsorted(bounds, prices))`. **Что продемонстрировать:** `searchsorted` и разницу `side`. **Вопросы:** что возвращает `searchsorted`; чем `side='left'` отличается от `side='right'` на границе; как `searchsorted` + `bincount` заменяют `histogram`; как работает O(log n).
"""
import numpy as np

bounds = np.array([0, 1_000_000, 2_000_000, 3_500_000, 5_000_000, 50_000_000])
prices = np.array([700_000, 1_450_000, 2_200_000, 3_200_000, 4_100_000, 6_000_000])
left = np.searchsorted(bounds, prices)
right = np.searchsorted(bounds, prices, side="right")
print("left :", left, "| right:", right)
print("частоты по категориям:", np.bincount(left, minlength=len(bounds)))
# searchsorted возвращает ПОЗИЦИЮ вставки в отсортированный bounds, сохраняющую порядок;
# позиция i означает «между bounds[i-1] и bounds[i]» -> номер категории.
# side='left' (по умолчанию): bounds[i-1] < x <= bounds[i]; side='right': bounds[i-1] <= x < bounds[i].
# Различие видно только когда значение РАВНО границе:
edge = np.array([2_000_000])
print("на границе 2M: left =", np.searchsorted(bounds, edge), "right =", np.searchsorted(bounds, edge, side="right"))
# searchsorted + bincount = гистограмма с произвольными границами (как np.histogram, но
# вы сами управляете краями/включением границ). Бинарный поиск делит диапазон пополам -
# O(log n) на элемент: для 1M чисел ~20 сравнений.
print("np.histogram:", np.histogram(prices, bins=bounds)[0])

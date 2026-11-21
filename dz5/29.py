"""
**Задача 29 (`lexsort` и многоуровневая сортировка).** Даны массивы `brands` (марки), `prices` (цены), `years` (годы выпуска). Отсортируйте:
- сначала по марке, потом по цене: `np.lexsort((prices, brands))`;
- сначала по цене, потом по году: `np.lexsort((years, prices))`.

Примените индексы ко всем массивам. **Что продемонстрировать:** многоуровневую сортировку. **Вопросы:** почему последний ключ в `lexsort` — основной; чем `lexsort` отличается от `np.argsort(structured, order=...)`; когда удобнее структурированный массив; как `lexsort` связан со стабильностью.
"""
import numpy as np

brands = np.array(["Toyota", "BMW", "Kia", "Toyota", "BMW", "Kia", "Toyota"])
prices = np.array([2_500_000, 5_500_000, 1_450_000, 2_300_000, 4_200_000, 1_450_000, 2_500_000])
years = np.array([2020, 2022, 2019, 2021, 2023, 2018, 2018])

i1 = np.lexsort((prices, brands))      # ПОСЛЕДНИЙ ключ (brands) - основной, prices - при равенстве марки
print("марка -> цена:")
for b, p, y in zip(brands[i1], prices[i1], years[i1]): print(f"  {b:7s} {p:>9,} {y}")
i2 = np.lexsort((years, prices))       # основной - цена, при равных ценах - год
print("цена -> год:")
for b, p, y in zip(brands[i2], prices[i2], years[i2]): print(f"  {b:7s} {p:>9,} {y}")
# Последний ключ - главный (как «сортировка по последнему столбцу, затем по предыдущему»;
# lexsort идёт последовательно от первого ключа к последнему устойчивыми сортировками).
# lexsort работает с отдельными массивами; структурированный массив + argsort(order=[...])
# удобнее, когда поля уже живут вместе (сортировка по именам полей в порядке приоритета).
rec = np.array(list(zip(brands, prices, years)), dtype=[("brand", "U10"), ("price", "i8"), ("year", "i4")])
print("structured order:", np.argsort(rec, order=["brand", "price"]), "== lexsort:", np.array_equal(np.argsort(rec, order=["brand", "price"]), i1))
# Стабильность: lexsort устойчив - при полном равенстве всех ключей сохраняется исходный порядок.

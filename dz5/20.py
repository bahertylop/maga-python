"""
**Задача 20 (broadcasting на практике: нормализация).** Дана матрица характеристик формы `(365, 5)` — 365 моделей × 5 характеристик (цена, мощность, расход, объём, масса). Вычислите:
- среднее по каждой характеристике (`data.mean(axis=0)`);
- стандартное отклонение (`data.std(axis=0)`);
- центрирование: `centered = data - data.mean(axis=0)`;
- стандартизацию: `standardized = centered / data.std(axis=0)`.

Проверьте, что после стандартизации среднее ≈ 0, std ≈ 1. **Что продемонстрировать:** центрирование и стандартизацию. **Вопросы:** почему работает без `reshape`; что при перепутывании `axis=0`/`axis=1`; как broadcasting экономит память; как то же самое через `keepdims=True`.
"""
import numpy as np

rng = np.random.default_rng(20)
data = rng.normal([2e6, 150, 8, 2.0, 1500], [5e5, 30, 2, 0.5, 200], size=(365, 5))   # цена, мощность, расход, объём, масса
mean, std = data.mean(axis=0), data.std(axis=0)
print("mean по характеристикам:", mean.round(1))
print("std  по характеристикам:", std.round(1))
centered = data - mean            # (365, 5) - (5,): среднее растягивается по 365 строкам
standardized = centered / std
print("после стандартизации mean ≈", standardized.mean(axis=0).round(10), "std ≈", standardized.std(axis=0).round(6))
# Работает без reshape: (5,) автоматически становится (1, 5) и растягивается по оси 0.
# Если перепутать axis: axis=1 даёт статистики по КАЖДОЙ модели (форма (365,)) - вычитать
# их из (365, 5) нельзя (ошибка broadcasting) - нужен keepdims. Broadcasting экономит память:
# не создаётся (365, 5)-копия среднего, значения «растягиваются» виртуально.
std1 = data.std(axis=1, keepdims=True)         # (365, 1) - можно делить построчно
mean1 = data.mean(axis=1, keepdims=True)
print("построчная нормировка shape:", ((data - mean1) / std1).shape)
std_k = data.std(axis=0, keepdims=True)         # то же через keepdims: форма (1, 5)
print("keepdims-вариант совпадает:", np.allclose(centered / std_k, standardized))

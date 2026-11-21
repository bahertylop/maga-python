"""
**Задача 8 (случайные числа, воспроизводимость).** Автосалон моделирует данные. Создайте `rng = np.random.default_rng(seed=42)`:
- 10 равномерных `rng.random(10)` — вероятности покупки;
- 10 нормальных `rng.normal(2000000, 500000, 10)` — цены автомобилей;
- 10 целых `rng.integers(2010, 2026, 10)` — годы выпуска.

Создайте второй генератор с тем же `seed=42` — значения совпадают. Третий без `seed` — значения другие. **Что продемонстрировать:** воспроизводимость. **Вопросы:** зачем `seed`; чем `default_rng` отличается от старого `np.random.seed`; как `SeedSequence` помогает для параллельных вычислений.
"""
import numpy as np

rng = np.random.default_rng(seed=42)
print("random      :", rng.random(10).round(3))
print("normal      :", rng.normal(2_000_000, 500_000, 10).round(0))
print("integers    :", rng.integers(2010, 2026, 10))

rng_a, rng_b = np.random.default_rng(42), np.random.default_rng(42)
print("одинаковый seed совпадает:", np.array_equal(rng_a.random(5), rng_b.random(5)))
print("без seed (разные запуски) :", np.random.default_rng().random(3).round(3))

# seed нужен для воспроизводимости: один и тот же код даёт одни и те же «случайные»
# числа (тесты, отчёты, отладка, публикации).
# default_rng - современный Generator (алгоритм PCG64): лучше статистика, быстрее,
# состояние инкапсулировано в объекте. Старый np.random.seed управляет ГЛОБАЛЬНЫМ
# состоянием (MT19937), которое делят все модули - трудно изолировать эксперименты.
# SeedSequence порождает независимые дочерние потоки: для параллельных вычислений
# каждому процессу даётся свой spawn - без перекрытия последовательностей.
ss = np.random.SeedSequence(42)
children = [np.random.default_rng(s) for s in ss.spawn(3)]
print("независимые потоки:", [round(c.random(), 3) for c in children])

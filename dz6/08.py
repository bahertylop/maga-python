r"""
**Задача 8 (воспроизводимость, sample).** Создайте `rng = np.random.default_rng(seed=42)` и DataFrame из 100 строк: `customer_id`, `purchase_prob` (uniform 0–1), `deal_amount` (normal 1500000±300000). Создайте второй генератор с `seed=42` — сравните. Третий без seed — сравните. Выполните `df.sample(n=5, random_state=42)` дважды. Ожидаемый вывод: два генератора с `seed=42` дают идентичные последовательности; третий без seed — другие; `df.sample(n=5, random_state=42)` возвращает одинаковые строки при повторных вызовах. В комментариях объясните: зачем нужен `seed` (воспроизводимость экспериментов, отладка); чем `default_rng` лучше `np.random.seed` (не глобальное состояние, потокобезопаснее); как `SeedSequence` помогает для параллельных вычислений (разные потоки — разные seed из одного родителя); чем `df.sample` отличается от `rng.choice` по работе с индексом (`sample` сохраняет исходный индекс, `choice` возвращает позиции); почему воспроизводимость критична в production (одинаковые тесты, аудит продаж); что произойдёт при `np.random.seed` в многопоточном коде (состояние гонки, непредсказуемые результаты).
"""
import numpy as np
import pandas as pd

def make(rng):
    return pd.DataFrame({"customer_id": np.arange(100), "purchase_prob": rng.random(100),
                         "deal_amount": rng.normal(1_500_000, 300_000, 100)})
a, b, c = make(np.random.default_rng(42)), make(np.random.default_rng(42)), make(np.random.default_rng())
print("seed=42 дважды идентичны:", a.equals(b), "| без seed:", a.equals(c))
s1, s2 = a.sample(n=5, random_state=42), a.sample(n=5, random_state=42)
print("sample(random_state=42) повторяется:", s1.equals(s2), "| индексы:", s1.index.tolist())
print("choice возвращает ПОЗИЦИИ:", np.random.default_rng(1).choice(100, 5, replace=False))
# seed нужен для воспроизводимости (тесты, отладка, аудит). default_rng хранит состояние ВНУТРИ объекта,
# а np.random.seed меняет ГЛОБАЛЬНОЕ состояние, которое делят все библиотеки и потоки -
# в многопоточном коде возникает гонка, и результаты непредсказуемы.
# SeedSequence.spawn(n) порождает n независимых дочерних seed из родителя - для параллельных воркеров.
children = [np.random.default_rng(s) for s in np.random.SeedSequence(42).spawn(3)]
print("независимые потоки:", [round(float(g.random()), 3) for g in children])
# df.sample сохраняет ИСХОДНЫЙ индекс строк (удобно для обратной привязки), rng.choice - позиции/значения.

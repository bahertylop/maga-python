"""
**Задача 35 (случайные числа и распределения).** Создайте `rng = np.random.default_rng(seed=42)`:
- 1000 нормальных цен (`rng.normal(2000000, 500000, 1000)`);
- 1000 равномерных годов выпуска (`rng.uniform(2000, 2025, 1000)`);
- 1000 биномиальных «продаж» (`rng.binomial(10, 0.3, 1000)`);
- 1000 пуассоновских «посетителей в день» (`rng.poisson(25, 1000)`).

Для каждого выведите среднее и std, сравните с теорией. Дополнительно: `rng.choice(100, size=10, replace=False)` — выборка без повторений; `rng.shuffle(showroom)`; `rng.permutation(10)`. **Что продемонстрировать:** распределения и статистики. **Вопросы:** чем `choice(replace=False)` отличается от `permutation`; зачем `SeedSequence`; почему `default_rng` лучше `np.random.seed`; как ограничить нормальные цены снизу нулём (через `clip` или `lognormal`).
"""
import numpy as np

rng = np.random.default_rng(seed=42)
samples = {
    "normal(2e6, 5e5)": (rng.normal(2_000_000, 500_000, 1000), 2_000_000, 500_000),
    "uniform(2000, 2025)": (rng.uniform(2000, 2025, 1000), 2012.5, 25 / np.sqrt(12)),
    "binomial(10, 0.3)": (rng.binomial(10, 0.3, 1000), 3.0, np.sqrt(10 * 0.3 * 0.7)),
    "poisson(25)": (rng.poisson(25, 1000), 25.0, 5.0),
}
for name, (x, m, s) in samples.items():
    print(f"{name:20s} mean={x.mean():12.2f} (теор. {m:12.2f})  std={x.std():10.2f} (теор. {s:10.2f})")

print("choice без повторов:", rng.choice(100, size=10, replace=False))
showroom = np.arange(10); rng.shuffle(showroom)         # shuffle - НА МЕСТЕ
print("shuffle:", showroom, "| permutation(10):", rng.permutation(10))
# choice(replace=False) - случайная ПОДВЫБОРКА размера k (можно k < n); permutation(n) -
# перемешивание ВСЕХ n элементов (результат - новый массив; shuffle - на месте).
# SeedSequence - независимые потоки для параллельных процессов; default_rng - новый
# Generator (PCG64): лучше статистические свойства, быстрее, нет глобального состояния.
# Нормальные цены могут быть отрицательными: clip(0) срезает хвост (создаёт «пик» на нуле),
# lognormal - всегда >0 и ближе к реальным ценам (правый хвост):
m, s = 2e6, 5e5
sig2 = np.log(1 + s ** 2 / m ** 2); mu = np.log(m) - sig2 / 2
ln = rng.lognormal(mu, np.sqrt(sig2), 1000)
print("lognormal min > 0:", ln.min() > 0, "| mean:", ln.mean().round(0))
print("clip:", np.clip(rng.normal(m, s, 1000), 0, None).min())

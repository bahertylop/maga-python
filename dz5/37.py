"""
**Задача 37 (операции на месте).** Дана матрица цен `prices` формы `(1000, 1000)`. Сравните:
- `prices = prices * 1.07` — новый массив;
- `prices *= 1.07` — на месте.

Замерьте время и `nbytes` до/после. Дополнительно: `np.multiply(prices, 1.07, out=prices)`; `np.clip(prices, 500000, 5000000, out=prices)`. **Что продемонстрировать:** экономию памяти и времени. **Вопросы:** почему `*=` быстрее и экономнее; почему `prices[:] = prices * 1.07` не экономит память; когда операции на месте вредны; как `out` связан с операциями на месте.
"""
import time
import tracemalloc
import numpy as np

rng = np.random.default_rng(37)
base = rng.uniform(5e5, 5e6, (1000, 1000))

def measure(label, fn, repeat=20):
    arr = base.copy()
    tracemalloc.start()
    t = time.perf_counter()
    for _ in range(repeat):
        arr = fn(arr)
    dt = (time.perf_counter() - t) / repeat
    peak = tracemalloc.get_traced_memory()[1] / 1e6
    tracemalloc.stop()
    print(f"{label:34s} {dt * 1e3:6.2f} мс  пик доп. памяти {peak:6.1f} МБ")

print("nbytes массива:", base.nbytes / 1e6, "МБ")
measure("prices = prices * 1.07 (новый)", lambda p: p * 1.07)
measure("prices *= 1.07 (на месте)", lambda p: p.__imul__(1.07))
measure("prices[:] = prices * 1.07", lambda p: (p.__setitem__(slice(None), p * 1.07), p)[1])
def mul_out(p): np.multiply(p, 1.07, out=p); return p
measure("np.multiply(..., out=prices)", mul_out)
def clip_out(p): np.clip(p, 5e5, 5e6, out=p); return p
measure("np.clip(..., out=prices)", clip_out)
# *= не создаёт временный массив (результат пишется прямо в буфер) - быстрее и экономит
# память. prices[:] = prices * 1.07 СНАЧАЛА вычисляет prices * 1.07 во временный массив
# (аллокация), и только потом копирует - память не экономится. out= - тот же механизм,
# что и *=. Вред: изменяются ВСЕ ссылки/виды на этот буфер (срезы, переданные функции),
# и исходные данные теряются; плюс при смене dtype (int *= 1.07) выбросит ошибку приведения типов.
a = np.arange(3)
try:
    a *= 1.07
except Exception as e:
    print("int-массив *= float ->", type(e).__name__)

"""
**Задача 27 (`partition` и `argpartition`).** Дан массив из 1 000 000 случайных цен. Найдите топ-10 самых дорогих:
- полная сортировка: `np.sort(prices)[-10:]`;
- `np.partition(prices, -10)[-10:]`;
- `np.argpartition(prices, -10)[-10:]`.

Замерьте время через `time.perf_counter()`. **Что продемонстрировать:** разницу во времени. **Вопросы:** почему `partition` — O(n), а `sort` — O(n log n); что гарантирует `partition`; во сколько раз быстрее для 1 000 000; почему `argpartition` + `argsort` дают корректный топ-N.
"""
import time
import numpy as np

rng = np.random.default_rng(27)
prices = rng.normal(2e6, 5e5, 1_000_000)

def timeit(fn, repeat=5):
    best = float("inf")
    for _ in range(repeat):
        t = time.perf_counter(); r = fn(); best = min(best, time.perf_counter() - t)
    return best, r

t_sort, top_sort = timeit(lambda: np.sort(prices)[-10:])
t_part, top_part = timeit(lambda: np.partition(prices, -10)[-10:])
t_argp, idx = timeit(lambda: np.argpartition(prices, -10)[-10:])
print(f"sort        : {t_sort * 1e3:7.2f} мс")
print(f"partition   : {t_part * 1e3:7.2f} мс  (в {t_sort / t_part:.1f} раз быстрее)")
print(f"argpartition: {t_argp * 1e3:7.2f} мс")
print("то же множество топ-10:", np.allclose(np.sort(top_part), top_sort))
# partition - алгоритм выбора (introselect), O(n): гарантирует лишь, что элемент на
# позиции kth стоит на своём месте, слева от него - не большие, справа - не меньшие; ПОРЯДОК
# внутри групп не определён. Полная сортировка - O(n log n). Для топ-N порядок
# внутри топа обычно не нужен. Если нужен упорядоченный топ: argpartition (O(n)) выбирает
# N кандидатов, затем argsort только их (O(N log N)):
top_idx = idx[np.argsort(prices[idx])[::-1]]
print("топ-10 по убыванию:", prices[top_idx].round(0)[:3], "...")

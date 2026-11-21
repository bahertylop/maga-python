"""
**Задача 23 (универсальные функции ufunc).** Дан массив цен `prices = np.array([2500000, 1800000, 3200000, 950000, 4100000])`. Примените:
- `np.add(prices, 50000)` — доп. оборудование;
- `np.multiply(prices, 1.07)` — инфляция 7%;
- `np.power(prices, 2)`;
- `np.sqrt(prices)`;
- `np.exp(prices / 10000000)`;
- `np.log(prices)`.

Используйте:
- `out` — запишите в заранее созданный массив;
- `where` — примените только там, где `prices > 2000000`.

**Что продемонстрировать:** вызовы ufunc и `out`/`where`. **Вопросы:** что такое ufunc; почему `np.add(a, b)` и `a + b` эквивалентны; зачем `out`/`where`; как ufunc связаны с broadcasting; когда `np.log` вернёт `-inf`/`nan`; назовите ещё ufunc (`np.sin`, `np.abs`, `np.maximum`, `np.mod`).
"""
import numpy as np

prices = np.array([2500000, 1800000, 3200000, 950000, 4100000])
print("add +50k  :", np.add(prices, 50_000))
print("*1.07     :", np.multiply(prices, 1.07))
print("power 2   :", np.power(prices, 2))
print("sqrt      :", np.sqrt(prices).round(1))
print("exp       :", np.exp(prices / 1e7).round(3))
print("log       :", np.log(prices).round(3))

out = np.empty_like(prices, dtype=float)          # out: результат пишется в готовый массив
np.multiply(prices, 1.07, out=out)
print("out:", out)
res = prices.astype(float)
np.multiply(prices, 1.07, out=res, where=prices > 2_000_000)    # применить только там, где True
print("where (остальные не тронуты):", res)
# ufunc - универсальная функция: векторизованная поэлементная функция над массивами
# (np.add, np.sin, np.abs, np.maximum, np.mod...). a + b == np.add(a, b) - оператор лишь
# сокращённая запись. ufunc поддерживают broadcasting. out/where экономят память и
# позволяют условную обработку. np.log(0) = -inf, np.log(-1) = nan (с предупреждением).
with np.errstate(divide="ignore", invalid="ignore"):
    print("log(0), log(-1):", np.log(0.0), np.log(-1.0))
print("ещё ufunc:", np.maximum(prices, 2_000_000), np.mod(prices, 1_000_000))

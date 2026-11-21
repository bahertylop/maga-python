"""
**Задача 24 (условная логика: `where`, `select`, `clip`).** Дан массив цен `prices = np.array([700000, 1450000, 1800000, 2500000, 3200000, 4100000, 5000000])`. Реализуйте:
- `np.where(prices < 1000000, 1000000, prices)` — поднимите минимальную цену;
- `np.where(prices > 4000000, 4000000, prices)` — обрежьте максимальную.

Для категоризации:
```python
conditions = [prices < 1500000, (prices >= 1500000) & (prices < 3000000), prices >= 3000000]
choices = ["бюджет", "средний", "премиум"]
categories = np.select(conditions, choices, default="?")
```
Наконец, `np.clip(prices, 1000000, 4000000)`. Дополнительно реализуйте `np.add.reduce` и `np.add.accumulate` для массива продаж `sales = np.array([12, 15, 11, 18, 14, 13, 16])`. **Что продемонстрировать:** все три подхода и методы ufunc. **Вопросы:** чем `where` отличается от `select`; почему `select` берёт первое условие; когда `clip` лучше `where`; чем `reduce` отличается от `accumulate`; что такое `identity` у ufunc.
"""
import numpy as np

prices = np.array([700000, 1450000, 1800000, 2500000, 3200000, 4100000, 5000000])
print("минимум 1M  :", np.where(prices < 1_000_000, 1_000_000, prices))
print("максимум 4M :", np.where(prices > 4_000_000, 4_000_000, prices))
conditions = [prices < 1_500_000, (prices >= 1_500_000) & (prices < 3_000_000), prices >= 3_000_000]
choices = ["бюджет", "средний", "премиум"]
categories = np.select(conditions, choices, default="?")
print("select:", categories)
print("clip   :", np.clip(prices, 1_000_000, 4_000_000))

sales = np.array([12, 15, 11, 18, 14, 13, 16])
print("add.reduce    :", np.add.reduce(sales), "(= sum)")
print("add.accumulate:", np.add.accumulate(sales), "(= cumsum)")
# where(cond, a, b) - выбор из ДВУХ вариантов; select - из НЕСКОЛЬКИХ по списку условий (как
# if/elif/else); при нескольких True берётся ПЕРВОЕ условие. clip лучше where для
# «обрезки» обоих концов одной командой (читабельнее и быстрее). reduce сворачивает массив
# в одно значение (применяя ufunc последовательно), accumulate возвращает ВСЕ промежуточные
# результаты. identity - нейтральный элемент операции: у add это 0, у multiply 1 (то, что вернёт
# reduce для пустого массива).
print("identity add/multiply:", np.add.identity, np.multiply.identity, "| reduce([]):", np.add.reduce(np.array([])))

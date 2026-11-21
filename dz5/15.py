"""
**Задача 15 (view vs copy).** Дан массив цен `prices = np.arange(10) * 100000 + 500000`. Создайте:
- `view = prices[2:5]`;
- `copy = prices[2:5].copy()`.

Измените `view[0] = 9999999` и `copy[0] = 1111111`. Выведите `prices`, `view`, `copy`. Проверьте:
- `view.base is prices` → `True`;
- `copy.base is None` → `True`;
- `np.shares_memory(prices, view)` → `True`;
- `np.shares_memory(prices, copy)` → `False`.

**Что продемонстрировать:** влияние view и независимость copy. **Вопросы:** почему NumPy возвращает view; когда это приводит к ошибкам (передача среза в функцию, которая меняет данные); как защититься; почему view экономит память, но опасен для больших массивов.
"""
import numpy as np

prices = np.arange(10) * 100000 + 500000
view = prices[2:5]
copy = prices[2:5].copy()
view[0] = 9_999_999
copy[0] = 1_111_111
print("prices:", prices)
print("view  :", view)
print("copy  :", copy)
print("view.base is prices          :", view.base is prices)
print("copy.base is None            :", copy.base is None)
print("shares_memory(prices, view)  :", np.shares_memory(prices, view))
print("shares_memory(prices, copy)  :", np.shares_memory(prices, copy))
# Почему view: не копируются данные - срез за O(1), без лишней памяти (важно для
# гигабайтных массивов). Опасность: функция, получившая срез, может ИЗМЕНИТЬ исходник
# (def f(a): a[0] = 0; f(prices[2:5]) портит prices). Защита: .copy() там, где нужна
# независимость; arr.flags.writeable = False для защиты от записи; осознанно документировать мутации.
def zero_first(a): a[0] = 0
tmp = prices[:3]; zero_first(tmp)
print("функция испортила исходник:", prices[:3])
ro = prices[:3]; ro.flags.writeable = False
try:
    ro[0] = 1
except ValueError as e:
    print("защита от записи ->", e)

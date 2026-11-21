"""
**Задача 17 (ravel и flatten).** Дана `sales` формы `(3, 4)`. Получите одномерный массив:
- `sales.ravel()`;
- `sales.flatten()`;
- `sales.reshape(-1)`.

Сравните `.base`. Измените элемент в `ravel` — `sales` изменилась; в `flatten` — не изменилась. **Что продемонстрировать:** view vs copy при уплощении. **Вопросы:** когда `ravel`, когда `flatten`; почему `flatten` медленнее; почему `ravel` иногда тоже возвращает копию.
"""
import numpy as np

sales = np.array([[120, 150, 90, 130], [110, 140, 100, 125], [130, 160, 95, 140]])
r = sales.ravel(); f = sales.flatten(); rs = sales.reshape(-1)
print("ravel.base is sales   :", r.base is sales, "| flatten.base:", f.base, "| reshape(-1).base is sales:", rs.base is sales)

r[0] = 999
print("после r[0]=999: sales[0,0] =", sales[0, 0], "(ravel - view, изменился)")
f[1] = -1
print("после f[1]=-1:  sales[0,1] =", sales[0, 1], "(flatten - копия, не изменился)")
# flatten ВСЕГДА копирует -> медленнее и дороже по памяти. ravel возвращает view, если
# массив C-непрерывен (можно «вытянуть» без перекладывания); иначе (транспонированный,
# срез с шагом) делает копию - тогда запись в него исходник НЕ меняет.
t = sales.T.ravel()
print("ravel транспонированного - копия:", t.base is None or t.base is not sales)
# Когда что: нужно только читать/вычислять - ravel; нужна независимая копия - flatten.

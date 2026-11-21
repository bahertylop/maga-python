"""
**Задача 40 (`einsum` и структурированные массивы).** Даны:
- `A` формы `(3, 4)` — «филиалы × марки»;
- `B` формы `(4, 5)` — «марки × месяцы»;
- `v` формы `(4,)` — веса марок.

Реализуйте через `np.einsum`:
- `A @ B`: `np.einsum('ik,kj->ij', A, B)`;
- `A @ v`: `np.einsum('ik,k->i', A, v)`;
- `v @ v`: `np.einsum('i,i->', v, v)`;
- внешнее `v` на себя: `np.einsum('i,j->ij', v, v)`;
- след: `np.einsum('ii->', M)`.

Дополнительно структурированный массив:
```python
sales_log = np.array([
    ('2025-01-01', 'Toyota', 'Camry', 2500000),
    ('2025-01-02', 'BMW', 'X5', 5500000),
    ('2025-01-03', 'Kia', 'Rio', 1450000),
], dtype=[('date', 'U10'), ('brand', 'U20'), ('model', 'U20'), ('price', 'i8')])
```
Вычислите среднюю цену (`sales_log['price'].mean()`) и отфильтруйте автомобили дороже 2 000 000. **Что продемонстрировать:** `einsum` для разных операций и работу со структурированным массивом. **Вопросы:** когда `einsum` читаемее, чем `@`; почему структурированные массивы не заменяют Pandas; как `einsum` обобщается на тензоры (`'bij,bjk->bik'`); как структурированный массив связан с `@dataclass` (оба хранят разнородные поля, но NumPy — C-структуры в памяти).
"""
import numpy as np

rng = np.random.default_rng(40)
A = rng.integers(1, 10, (3, 4)); B = rng.integers(1, 10, (4, 5)); v = rng.integers(1, 5, 4).astype(float)
M = rng.integers(1, 10, (4, 4))
print("A@B     :", np.allclose(np.einsum("ik,kj->ij", A, B), A @ B))
print("A@v     :", np.allclose(np.einsum("ik,k->i", A, v), A @ v))
print("v·v     :", np.einsum("i,i->", v, v), "==", v @ v)
print("outer   :", np.allclose(np.einsum("i,j->ij", v, v), np.outer(v, v)))
print("trace   :", np.einsum("ii->", M), "==", np.trace(M))
# einsum читаемее @, когда операция нетривиальна (суммирование по нескольким осям, диагонали,
# транспонирование «на лету»). Формула 'индексы входов->выход': индексы, которых нет справа,
# суммируются. Обобщается на тензоры: пакет матриц 'bij,bjk->bik' (batch matmul).
X = rng.random((8, 3, 4)); Y = rng.random((8, 4, 2))
print("batch matmul:", np.allclose(np.einsum("bij,bjk->bik", X, Y), X @ Y), np.einsum("bij,bjk->bik", X, Y).shape)

sales_log = np.array([
    ("2025-01-01", "Toyota", "Camry", 2500000),
    ("2025-01-02", "BMW", "X5", 5500000),
    ("2025-01-03", "Kia", "Rio", 1450000),
], dtype=[("date", "U10"), ("brand", "U20"), ("model", "U20"), ("price", "i8")])
print("средняя цена:", sales_log["price"].mean())
print("дороже 2M:", sales_log[sales_log["price"] > 2_000_000])
# Структурированные массивы не заменяют Pandas: нет индексов, groupby, слияний, удобной
# работы с пропусками. Они хранят разнородные поля как C-структуры в ОДНОМ буфере памяти
# (как @dataclass хранит поля, но компактно и векторно, без объектов Python на каждую запись).
print("itemsize записи:", sales_log.dtype.itemsize, "байт")

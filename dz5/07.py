"""
**Задача 7 (память: itemsize и nbytes).** Автосалон хранит данные о 1 000 000 сделок. Сравните память:
- `float64` — суммы сделок;
- `float32` — те же суммы;
- `uint16` — количество проданных машин за день (0–65535).

Выведите `itemsize`, `nbytes` в МБ. Дополнительно оцените Python-список из 1 000 000 чисел через `sys.getsizeof` и сравните. **Что продемонстрировать:** разницу памяти. **Вопросы:** почему `nbytes` не включает метаданные; почему для больших массивов это критично; во сколько раз `uint16` экономнее `float64`.
"""
import sys
import numpy as np

n = 1_000_000
rng = np.random.default_rng(7)
amounts64 = rng.normal(2e6, 5e5, n)                 # float64
amounts32 = amounts64.astype(np.float32)            # те же суммы
cars_day = rng.integers(0, 65536, n).astype(np.uint16)

MB = 1024 ** 2
for name, a in (("float64", amounts64), ("float32", amounts32), ("uint16", cars_day)):
    print(f"{name}: itemsize={a.itemsize} Б, nbytes={a.nbytes / MB:.2f} МБ")

lst = amounts64.tolist()
list_size = sys.getsizeof(lst) + sum(sys.getsizeof(x) for x in lst)   # массив указателей + объекты float
print(f"Python-список: ~{list_size / MB:.1f} МБ (указатели + {n} объектов float по {sys.getsizeof(1.0)} Б)")
print(f"список / float64-массив: {list_size / amounts64.nbytes:.1f}x")
print(f"uint16 экономнее float64 в {amounts64.nbytes / cars_day.nbytes:.0f} раза")
# nbytes = size * itemsize - только БУФЕР данных; метаданные массива (shape, strides,
# dtype, флаги, ~100 байт заголовка) не входят (sys.getsizeof(arr) добавит их).
# Для больших массивов критично: память ограничена, а расход растёт линейно с n; 1 млрд
# float64 = 8 ГБ против 2 ГБ для float16/uint16, + кэш процессора работает лучше с компактными данными.

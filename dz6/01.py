r"""
**Задача 1 (создание Series, dtype, shape/size/ndim).** Автосалон ведёт учёт цен на 7 автомобилей: `[2500000, 1800000, 1200000, 950000, 3100000, 1500000, 2200000]` рублей. Создайте `pd.Series` из этих значений. Выведите `dtype`, `itemsize`, `shape`, `nbytes`. Дополнительно создайте второй Series из тех же значений с типом `float32` через `astype("float32")` и сравните `dtype`, `itemsize`, `nbytes` с первым. Ожидаемый вывод: для первого — `dtype=int64`, `itemsize=8`, `shape=(7,)`, `nbytes=56`; для второго — `dtype=float32`, `itemsize=4`, `nbytes=28`. В комментариях объясните: почему Pandas выбрал `int64`, а не `int32`; почему `shape` у одномерного Series — кортеж `(7,)`, а не `(7)`; что вернёт `prices.iloc[7]` и почему; как связаны `itemsize`, `nbytes` и `size`; во сколько раз `float32` экономнее `float64` и в каких случаях эта экономия критична (например, при хранении 10 млн записей о продажах за год); почему `astype("float32")` создаёт новый объект, а не меняет исходный Series на месте.
"""
import pandas as pd

prices = pd.Series([2500000, 1800000, 1200000, 950000, 3100000, 1500000, 2200000])
p32 = prices.astype("float32")
for name, s in (("int", prices), ("float32", p32)):
    # Series.itemsize удалён в Pandas 3 - берём размер элемента из dtype
    print(f"{name:8s} dtype={s.dtype} itemsize={s.dtype.itemsize} shape={s.shape} size={s.size} nbytes={s.nbytes}")

# int64, а не int32: Pandas опирается на NumPy, где целые Python-числа по умолчанию -
# платформенный int (int64 на 64-битных ОС); значения вмещаются, и «экономить» бит библиотека не пытается.
# shape - кортеж (7,): одноэлементный кортеж пишется с запятой, (7) - просто число.
# size = число элементов, nbytes = size * itemsize (7 * 8 = 56; у float32 7 * 4 = 28).
try:
    prices.iloc[7]                         # позиций 0..6 -> IndexError
except IndexError as e:
    print("prices.iloc[7] ->", type(e).__name__, e)
# float32 вдвое экономнее float64: при 10 млн записей это 40 МБ вместо 80 МБ на столбец
# (критично при десятках столбцов и ограниченной RAM); цена - точность ~7 десятичных знаков.
# astype создаёт НОВЫЙ объект (исходный Series не меняется): так безопаснее, а Copy-on-Write
# в Pandas 3 гарантирует независимость результата.
print("исходный не изменился:", prices.dtype, "| новый:", p32.dtype)

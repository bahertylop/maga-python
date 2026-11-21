r"""
**Задача 45 (to_numpy/values/NumPy).** Примените `df.to_numpy()`, `df.to_numpy(dtype="float32")`, `df.to_numpy(copy=True)`, `df.values`. Создайте DataFrame из NumPy с разнородными типами (числа + строки). Примените `df.select_dtypes(include=[np.number]).to_numpy()`. Создайте NumPy-массив из Series, передайте в `LinearRegression`. Ожидаемый вывод: `df.to_numpy()` на смешанном DataFrame даёт `object`; `select_dtypes(include=[np.number])` сохраняет числовые типы; `to_numpy(copy=True)` создаёт независимую копию. В комментариях объясните: почему `.values` устарел (может вернуть view или копию непредсказуемо); как `copy=False` делит память (изменения в массиве влияют на DataFrame); когда `select_dtypes` спасает (перед ML-моделью для прогноза цены автомобиля); что произойдёт при `.to_numpy` с пропусками (`NaN` или `pd.NA`); как `dtype` влияет на память; почему `to_numpy` на `category` возвращает `object` (раскодирует категории).
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

num = pd.DataFrame({"price": [1.0, 2.0, 3.0], "mileage": [10, 20, 30]})
print(num.to_numpy().dtype, "| float32:", num.to_numpy(dtype="float32").dtype, "| values:", type(num.values).__name__)
mixed = pd.DataFrame({"brand": ["Kia", "BMW", "Audi"], "price": [1.5, 2.5, 3.5]})
print("смешанный:", mixed.to_numpy().dtype, "| numeric only:", mixed.select_dtypes(include=[np.number]).to_numpy().dtype)
cp = num.to_numpy(copy=True); cp[0, 0] = 999; print("copy=True не влияет на df:", num.iloc[0, 0])
fl = pd.DataFrame({"a": [1.0, 2.0], "b": [3.0, 4.0]}); print("writeable: to_numpy() =", fl.to_numpy().flags.writeable, "| to_numpy(copy=False) =", fl.to_numpy(copy=False).flags.writeable, "| to_numpy(copy=True) =", fl.to_numpy(copy=True).flags.writeable, "(CoW: view только для чтения)")
with_na = pd.DataFrame({"a": [1, None, 3]}); print("NaN:", with_na.to_numpy().tolist(), "| Int64 + NA -> dtype", pd.DataFrame({"a": pd.array([1, None, 3], dtype="Int64")}).to_numpy().dtype, "| dtype=object:", pd.DataFrame({"a": pd.array([1, None, 3], dtype="Int64")}).to_numpy(dtype=object).tolist(), "| na_value=-1:", pd.DataFrame({"a": pd.array([1, None, 3], dtype="Int64")}).to_numpy(na_value=-1).tolist())
print("category.to_numpy:", pd.Series(["a", "b"], dtype="category").to_numpy().dtype, "| float32 экономит:", num.to_numpy(dtype="float32").nbytes, "vs", num.to_numpy().nbytes)
X = np.array([[10], [20], [30], [40]]); y = pd.Series([1.0, 2.0, 3.0, 4.0]).to_numpy()
mdl = LinearRegression().fit(X, y); print("коэф:", mdl.coef_.round(3), "| прогноз(50):", mdl.predict([[50]]).round(2))
# .values официально не deprecated, но поведение не гарантировано (view или копия, ExtensionArray -> разные типы); to_numpy
# явно управляет dtype/copy/na_value. В Pandas 3 при Copy-on-Write массив из to_numpy() без copy=True - read-only (writeable=False),
# т.е. изменить DataFrame «через массив» нельзя. select_dtypes нужен перед ML-моделью: нечисловые столбцы (brand) дают object.
# Пропуски: float -> NaN; nullable Int64 с NA -> float64 с NaN (или dtype=object оставит pd.NA, или задайте na_value=...). category -> массив значений (object/str), а не кодов.
# Меньший dtype (float32) вдвое уменьшает память.

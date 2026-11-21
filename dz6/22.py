r"""
**Задача 22 (базовый .str).** Создайте Series названий моделей автомобилей. Примените `.str.lower()`, `.str.upper()`, `.str.title()`, `.str.strip()`, `.str.len()`, `.str.contains("abc", na=False)`, `.str.startswith("Toyota")`, `.str.endswith("1")`, `.str.fullmatch(r"\d{4}")`. Проверьте `is_string_dtype()` перед применением. Попробуйте `.str.lower()` на числовом столбце. Ожидаемый вывод: `.str.len()` возвращает длину каждой строки; `.str.contains("abc", na=False)` на `NaN` возвращает `False`; `.str.lower()` на числовом — `AttributeError`. В комментариях объясните: почему `.str` не работает с числовым столбцом (нужен `.astype(str)`); почему `na=False` критичен (иначе `NaN` пропагируется); чем `fullmatch` отличается от `contains` (полное совпадение vs подстрока); как `.str.len()` обрабатывает `NaN` (возвращает `NaN`); в каких случаях `casefold` предпочтительнее `lower` (для Unicode, например, немецкая ß); что произойдёт при `.str` к `category`-столбцу (работает, если категории строковые, иначе `AttributeError`).
"""
import pandas as pd
from pandas.api.types import is_string_dtype

m = pd.Series(["Toyota Camry", "  bmw x5 ", None, "Kia Rio 1", "2024"])
print("is_string_dtype:", is_string_dtype(m))
print("lower:", m.str.lower().tolist()); print("title:", m.str.title().tolist()); print("strip:", m.str.strip().tolist())
print("len:", m.str.len().tolist(), "(NaN для None)")
print("contains(na=False):", m.str.contains("abc", na=False).tolist(), "| startswith:", m.str.startswith("Toyota").fillna(False).tolist())
print("endswith('1'):", m.str.endswith("1").fillna(False).tolist(), "| fullmatch:", m.str.fullmatch(r"\d{4}").fillna(False).tolist())
try:
    pd.Series([1, 2, 3]).str.lower()
except AttributeError as e:
    print(".str на числах ->", e)
print("astype(str).str.len():", pd.Series([1, 22]).astype(str).str.len().tolist())
print("casefold:", pd.Series(["Straße"]).str.casefold().tolist(), "vs lower:", pd.Series(["Straße"]).str.lower().tolist())
cat = pd.Series(["a", "b"], dtype="category")
print(".str на category со строками:", cat.str.upper().tolist())
# .str работает только со строковыми значениями (числа - через .astype(str)). na=False нужен, чтобы пропуск не превращал маску
# в NaN. fullmatch требует совпадения ВСЕЙ строки, contains - подстроки. casefold агрессивнее lower (для Unicode: ß -> ss).
# На category .str работает, если категории - строки; иначе AttributeError.

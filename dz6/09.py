r"""
**Задача 9 (чтение CSV в деталях).** Создайте CSV продаж с разделителем `;`, кодировкой `utf-8`, пропусками `["", "NA", "-"]`. Прочитайте через `read_csv` с параметрами: `sep=";"`, `encoding="utf-8"`, `dtype={"sale_id": "int32"}`, `parse_dates=["sale_date"]`, `usecols=["sale_id", "sale_date", "amount"]`, `nrows=10`, `na_values=["", "NA", "-"]`. Создайте второй CSV с десятичной запятой — прочитайте с `decimal=","`. Прочитайте первый без `dtype` — сравните типы. Ожидаемый вывод: с `dtype` столбец `sale_id` — `int32`, без — `int64`; `parse_dates` даёт `datetime64[us]`, без — `str`; `decimal=","` корректно преобразует `"123,45"` в `123.45`. В комментариях объясните: почему `dtype` при чтении эффективнее `astype` после (не создаётся промежуточный `object`-столбец, меньше памяти); когда `nrows` полезен для тестирования (быстрая проверка структуры); как `skiprows` пропускает метаданные (например, шапку отчёта салона); что произойдёт при неверной кодировке (`UnicodeDecodeError` или «кракозябры»); почему `na_values` нужно указывать явно (иначе `"NA"` может остаться строкой); как `decimal=","` влияет на тип результирующего столбца (`float64`).
"""
import io
import numpy as np
import pandas as pd
from pathlib import Path

HERE = Path(__file__).parent
raw = "report: sales\nsale_id;sale_date;amount;comment\n1;2025-01-10;1500,50;ok\n2;2025-01-11;-;NA\n3;2025-01-12;2300,00;\n"
p = HERE / "sales_semicolon.csv"; p.write_text(raw, encoding="utf-8")

kw = dict(sep=";", encoding="utf-8", skiprows=1, na_values=["", "NA", "-"], decimal=",")
df = pd.read_csv(p, dtype={"sale_id": "int32"}, parse_dates=["sale_date"], usecols=["sale_id", "sale_date", "amount"], nrows=10, **kw)
print(df.dtypes.to_dict(), "\n", df)
plain = pd.read_csv(p, **kw)
print("без dtype/parse_dates:", plain.dtypes.to_dict())
print("decimal=',' -> amount float64:", plain["amount"].tolist())
print("без decimal=',':", pd.read_csv(p, sep=";", skiprows=1)["amount"].tolist(), "(строки!)")
p.write_bytes("sale_id;город\n1;Москва\n".encode("cp1251"))
try:
    pd.read_csv(p, sep=";", encoding="utf-8")
except UnicodeDecodeError as e:
    print("неверная кодировка ->", type(e).__name__)
print("cp1251 корректно:", pd.read_csv(p, sep=";", encoding="cp1251").columns.tolist())
p.unlink()
# dtype при чтении эффективнее astype после: столбец сразу создаётся нужного типа, без промежуточного
# int64/object (меньше пик памяти). nrows - быстрая проверка структуры огромного файла.
# skiprows пропускает «шапку» отчёта (метаданные до заголовка). na_values указывайте явно: иначе "-"/"NA" может
# остаться строкой и столбец станет str. decimal="," превращает "1500,50" в float 1500.5.

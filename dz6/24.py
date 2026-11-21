r"""
**Задача 24 (.str.replace/cat/pad/zfill).** Создайте Series email клиентов. Примените `.str.replace("@.*", "", regex=True)`. Сравните `.str.replace("f.", "ba", regex=False)` и `regex=True`. Примените `.str.replace({"apple": "груша", "banana": "банан"})`. Примените `.str.cat(series2, sep=" ")` и `.str.cat(series2, sep=" ", na_rep="?")`. Примените `.str.pad(10, side="left", fillchar="0")` и `.str.zfill(6)`. Ожидаемый вывод: `regex=True` даёт `"foo" → "bao"`, `regex=False` — без изменений; `na_rep="?"` заполняет пропуски; `zfill(6)` дополняет нулями слева. В комментариях объясните: почему `regex=True` нужно указывать явно (в Pandas 3.0 поведение по умолчанию изменено на `False`); как `na_rep` обрабатывает пропуски; чем `zfill` отличается от `pad` (`zfill` — только нули слева, `pad` — гибко); как `replace` со словарём работает с несколькими паттернами; что произойдёт при `replace` с неверным паттерном (`re.error`); как `isalpha` обрабатывает кириллицу (возвращает `True` для букв).
"""
import pandas as pd

email = pd.Series(["anna@mail.ru", "boris@ya.ru", None])
print("replace('@.*'):", email.str.replace("@.*", "", regex=True).tolist())
f = pd.Series(["foo"])
print("regex=False:", f.str.replace("f.", "ba", regex=False).tolist(), "| regex=True:", f.str.replace("f.", "ba", regex=True).tolist())
try:
    print("словарь:", pd.Series(["apple", "banana"]).str.replace({"apple": "груша", "banana": "банан"}).tolist())
except (TypeError, ValueError) as e:
    print("str.replace со словарём не поддерживается в этой версии:", type(e).__name__)
s2 = pd.Series(["ru", "com", "org"])
print("cat:", email.str.cat(s2, sep=" ").tolist(), "| na_rep:", email.str.cat(s2, sep=" ", na_rep="?").tolist())
print("pad:", pd.Series(["42"]).str.pad(10, side="left", fillchar="0").tolist(), "| zfill:", pd.Series(["42"]).str.zfill(6).tolist())
try:
    pd.Series(["a"]).str.replace("(", "x", regex=True)
except Exception as e:
    print("неверный паттерн ->", type(e).__name__)
print("isalpha для кириллицы:", pd.Series(["Привет", "ab1"]).str.isalpha().tolist())
# В Pandas 3.0 regex по умолчанию False (раньше был True) - поэтому regex=True задают явно. na_rep подставляется вместо пропуска
# при склейке (иначе результат NaN). zfill - только нули слева (знак числа учитывается), pad - произвольный символ и сторона.
# Неверное регулярное выражение -> re.error (PatternError). isalpha распознаёт буквы Unicode, в том числе кириллицу.

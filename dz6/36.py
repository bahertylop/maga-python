r"""
**Задача 36 (tz_localize/tz_convert).** Создайте `DatetimeIndex` без пояса (время продажи). Примените `tz_localize("UTC")` и `tz_convert("Europe/Moscow")`. Убедитесь, что моменты совпадают (`ts_utc == ts_msk`). Создайте `pd.date_range("2024-01-01", periods=3, freq="D", tz="UTC")`. Используйте `zoneinfo.available_timezones()`. Попробуйте `tz_convert` на naive-данных. Ожидаемый вывод: `tz_localize("UTC")` добавляет `+00:00`; `tz_convert("Europe/Moscow")` сдвигает на `+03:00`; сравнение `ts_utc == ts_msk` — `True`; `tz_convert` на naive — `TypeError`. В комментариях объясните: почему `tz_convert` нельзя на naive-данных (неясно, из какой зоны конвертировать); чем `tz_localize` отличается от `tz_convert` (назначить зону vs пересчитать в другую); почему в 3.0 используется `zoneinfo` (стандартная библиотека вместо `pytz`); что произойдёт при `tz_localize` в зоне с DST (неоднозначное/несуществующее время); как `ambiguous` и `nonexistent` обрабатывают переходы; как сравнить два tz-aware Timestamp (автоматически приводятся к UTC).
"""
import pandas as pd
from zoneinfo import available_timezones

naive = pd.date_range("2025-01-15 10:00", periods=3, freq="h")
utc = naive.tz_localize("UTC"); msk = utc.tz_convert("Europe/Moscow")
print(utc[0], "->", msk[0], "| равны как моменты:", bool((utc == msk).all()))
print(pd.date_range("2024-01-01", periods=3, freq="D", tz="UTC")[0])
print("зон в zoneinfo:", len(available_timezones()), "| Europe/Moscow есть:", "Europe/Moscow" in available_timezones())
try:
    naive.tz_convert("Europe/Moscow")
except TypeError as e:
    print("tz_convert на naive ->", e)
# DST: 2025-10-26 в Берлине 02:30 бывает дважды, 2025-03-30 02:30 не существует
amb = pd.DatetimeIndex(["2025-10-26 02:30"])
try:
    amb.tz_localize("Europe/Berlin")
except Exception as e:
    print("неоднозначное время ->", type(e).__name__)
print("ambiguous='NaT':", amb.tz_localize("Europe/Berlin", ambiguous="NaT")[0], "| ambiguous=[True]:", amb.tz_localize("Europe/Berlin", ambiguous=[True])[0])
non = pd.DatetimeIndex(["2025-03-30 02:30"])
print("nonexistent='shift_forward':", non.tz_localize("Europe/Berlin", nonexistent="shift_forward")[0])
print("сравнение tz-aware:", pd.Timestamp("2025-01-01 12:00", tz="UTC") == pd.Timestamp("2025-01-01 15:00", tz="Europe/Moscow"))
# tz_convert нельзя на naive: непонятно, ИЗ какой зоны конвертировать - сначала tz_localize. tz_localize НАЗНАЧАЕТ зону (меняет смысл
# локального времени), tz_convert ПЕРЕСЧИТЫВАЕТ момент в другую зону (момент тот же). В 3.0 zoneinfo (стандартная библиотека)
# вместо pytz. При DST: ambiguous (повторяющийся час) и nonexistent (пропущенный час) определяют, что делать с такими метками.
# Два tz-aware Timestamp сравниваются как абсолютные моменты (приводятся к UTC).

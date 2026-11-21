r"""
**Задача 33 (Timestamp/Timedelta/Period).** Создайте `pd.Timestamp("2025-01-15 14:30")` (время продажи) — извлеките `year`, `month`, `day`, `hour`, `dayofweek`, `day_name()`, `is_month_end`. Прибавьте `pd.Timedelta(days=5)`. Создайте `pd.Timedelta("3 days 2 hours")` — выведите `total_seconds()`. Создайте `pd.Period("2025-01", freq="M")` — выведите `start_time`, `end_time`, прибавьте `3`. Примените `pd.to_datetime(["2025-01-01", "invalid"], errors="coerce")`. Ожидаемый вывод: `Timestamp("2025-01-15").day_name()` = `"Wednesday"`; `Timedelta("3 days 2 hours").total_seconds()` = `266400.0`; `Period("2025-01") + 3` = `Period("2025-04", "M")`; `to_datetime(errors="coerce")` даёт `[Timestamp, NaT]`. В комментариях объясните: чем `Period` отличается от `Timestamp` (период vs момент); почему `errors="coerce"` безопаснее `raise` (не ломает пайплайн); чем `Timedelta` отличается от `Period` (длительность vs календарный период); как `Period` обрабатывает границы месяца (start_time/end_time); что произойдёт при `to_datetime` с неверным форматом без `errors` (`ValueError`); как `Timestamp` работает с часовыми поясами (`tz_localize`/`tz_convert`).
"""
import pandas as pd

t = pd.Timestamp("2025-01-15 14:30")
print(t.year, t.month, t.day, t.hour, t.dayofweek, t.day_name(), t.is_month_end)
print("+5 дней:", t + pd.Timedelta(days=5))
td = pd.Timedelta("3 days 2 hours"); print("total_seconds:", td.total_seconds())
p = pd.Period("2025-01", freq="M")
print(p.start_time, p.end_time, "| +3:", p + 3)
print(pd.to_datetime(["2025-01-01", "invalid"], errors="coerce").tolist())
try:
    pd.to_datetime(["2025-01-01", "invalid"])
except ValueError as e:
    print("без errors ->", type(e).__name__)
tz = t.tz_localize("Europe/Moscow"); print("tz_localize:", tz, "| tz_convert UTC:", tz.tz_convert("UTC"))
# Timestamp - МОМЕНТ времени, Period - календарный ПЕРИОД (месяц, квартал) с началом и концом, Timedelta - ДЛИТЕЛЬНОСТЬ.
# Period хранит границы (start_time/end_time = 1 янв 00:00 .. 31 янв 23:59:59.999...), сложение сдвигает на целые периоды.
# errors="coerce" не ломает пайплайн: плохие значения -> NaT. Без errors неверный формат -> ValueError.
# tz_localize назначает зону naive-времени, tz_convert пересчитывает tz-aware время в другую зону.

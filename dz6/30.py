r"""
**Задача 30 (expanding/ewm/groupby().rolling()).** Примените `expanding().mean()` и `expanding().sum()`. Примените `ewm(span=10).mean()`, `ewm(halflife=5).mean()`, `ewm(alpha=0.3).mean()`, `ewm(span=10, adjust=False).mean()`. Сравните влияние параметров. Примените `groupby("model")["sales"].transform(lambda x: x.rolling(7).mean())`. Ожидаемый вывод: `expanding` даёт накопительное среднее; `span=10` соответствует `α=2/11≈0.18`; `adjust=False` даёт другую формулу (рекурсивную); `groupby().rolling()` возвращает Series с исходным индексом через `transform`. В комментариях объясните: чем `expanding` отличается от `rolling` (накопительное окно от начала vs скользящее фиксированное); как `adjust=False` меняет формулу (рекурсивное взвешивание без деления на сумму весов); почему `transform` нужен для `groupby().rolling()` (чтобы вернуть исходную форму); как `halflife` связан с `span` (`halflife = ln(2)/α`, `span = 2/α - 1`); что произойдёт при `ewm` без параметров (`span=1` по умолчанию); как `ignore_na=True` влияет на результат (пропуски не влияют на веса).
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(30)
idx = pd.date_range("2025-01-01", periods=60)
s = pd.Series(rng.integers(5, 30, 60).astype(float), index=idx)
print("expanding mean/sum (последний):", s.expanding().mean().iloc[-1].round(2), s.expanding().sum().iloc[-1], "== общее:", s.mean().round(2), s.sum())
for label, kw in (("span=10", dict(span=10)), ("halflife=5", dict(halflife=5)), ("alpha=0.3", dict(alpha=0.3)), ("span=10, adjust=False", dict(span=10, adjust=False))):
    print(f"ewm {label:22s}", s.ewm(**kw).mean().iloc[-1].round(3))
print("span=10 -> alpha =", round(2 / (10 + 1), 3))
na = s.copy(); na.iloc[20:30] = np.nan
print("ignore_na False/True:", na.ewm(span=10).mean().iloc[-1].round(3), na.ewm(span=10, ignore_na=True).mean().iloc[-1].round(3))
try:
    s.ewm().mean()
except ValueError as e:
    print("ewm() без параметров ->", e)
d = pd.DataFrame({"model": rng.choice(["Camry", "Rio"], 60), "sales": s.values}, index=idx)
d["ma7"] = d.groupby("model")["sales"].transform(lambda x: x.rolling(7).mean())
print("groupby+transform сохраняет индекс/длину:", len(d["ma7"]) == len(d))
# expanding - окно растёт от начала (накопительное), rolling - фиксированное скользящее. span=2/alpha-1 -> alpha=2/(span+1);
# halflife = ln(0.5)/ln(1-alpha). adjust=False - рекурсивная формула y_t = (1-a)y_{t-1} + a x_t без нормировки на сумму весов;
# adjust=True (по умолчанию) делит на сумму весов (корректнее на коротком начале ряда). groupby().rolling() возвращает MultiIndex,
# поэтому transform нужен, чтобы вернуть результат в исходной форме. ewm без параметров -> ошибка (нужен span/com/halflife/alpha).

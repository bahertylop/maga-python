r"""
**Задача 53 (векторизация vs iterrows).** Создайте DataFrame из 100 000 строк с `price`, `discount`. Реализуйте `final_price = price * (1 - discount)` через `iterrows()`, `itertuples()`, `apply(axis=1)`, векторизацию `df["price"] * (1 - df["discount"])`. Замерьте время через `time.perf_counter()` (прогрев + 5 замеров). Сравните `np.where(df["final_price"] > 1500000, "премиум", "стандарт")` с `df["final_price"].apply(lambda x: ...)`. Ожидаемый вывод: `iterrows` ≈2.8 с, `itertuples` ≈0.09 с, `apply` ≈1.5 с, векторизация ≈0.001 с; ускорение векторизации относительно `iterrows` ≈2500×. В комментариях объясните: почему `iterrows` — антипаттерн (создаёт Series на каждую строку); когда `itertuples` уместен (когда нужны именованные кортежи); почему `apply(axis=1)` медленнее векторизации (Python-цикл); как `np.where` заменяет `apply`; что такое `namedtuple` (возвращает `itertuples`); как измерить время корректно (прогрев, несколько прогонов, `perf_counter`).
"""
import time
import numpy as np
import pandas as pd

rng = np.random.default_rng(53)
N = 100_000
df = pd.DataFrame({"price": rng.integers(500_000, 5_000_000, N).astype(float), "discount": rng.uniform(0, 0.2, N)})
def f_iterrows():
    return pd.Series([row["price"] * (1 - row["discount"]) for _, row in df.iterrows()])
def f_itertuples():
    return pd.Series([r.price * (1 - r.discount) for r in df.itertuples()])
def f_apply():
    return df.apply(lambda r: r["price"] * (1 - r["discount"]), axis=1)
def f_vec():
    return df["price"] * (1 - df["discount"])
def bench(f, repeats):
    f()   # прогрев (кэши, ленивые инициализации)
    ts = []
    for _ in range(repeats):
        t0 = time.perf_counter(); f(); ts.append(time.perf_counter() - t0)
    return min(ts), float(np.median(ts))
res = {}
for name, f, rep in (("iterrows", f_iterrows, 2), ("itertuples", f_itertuples, 3), ("apply(axis=1)", f_apply, 2), ("векторизация", f_vec, 5)):
    res[name] = bench(f, rep); print(f"{name:14s} min={res[name][0]*1e3:9.2f} мс, медиана={res[name][1]*1e3:9.2f} мс")
print(f"ускорение векторизации относительно iterrows: ~{res['iterrows'][0] / res['векторизация'][0]:.0f}x")
assert np.allclose(f_iterrows(), f_vec())
df["final_price"] = f_vec()
a = np.where(df["final_price"] > 1_500_000, "премиум", "стандарт")
b = df["final_price"].apply(lambda x: "премиум" if x > 1_500_000 else "стандарт")
print("np.where == apply:", (a == b.to_numpy()).all(), "| время np.where:", f"{bench(lambda: np.where(df['final_price'] > 1_500_000, 'премиум', 'стандарт'), 5)[0]*1e3:.1f} мс", "| apply:", f"{bench(lambda: df['final_price'].apply(lambda x: 'премиум' if x > 1_500_000 else 'стандарт'), 2)[0]*1e3:.1f} мс")
print("тип строки itertuples:", type(next(df.itertuples())).__name__)
# Цифры из задания (2.8 с / 0.09 с / 1.5 с / 0.001 с) зависят от машины - важен порядок: векторизация на порядки быстрее циклов.
# iterrows - антипаттерн: на КАЖДУЮ строку создаётся Series (в т.ч. приведение dtype всех столбцов к общему) - дорого.
# itertuples возвращает namedtuple (Pandas(Index=0, price=..., discount=...)): доступ по имени r.price, без создания Series -> намного быстрее.
# apply(axis=1) - всё тот же Python-цикл + создание Series на строку. Векторизация идёт в C-коде над целыми столбцами.
# np.where заменяет apply с условием (применяет условие ко всему массиву сразу). Корректное измерение: прогрев (первый вызов
# не считаем), несколько повторов, perf_counter (монотонные часы высокого разрешения), min или медиана. Для медленных методов
# число повторов уменьшено (2-3), чтобы скрипт не работал минутами.

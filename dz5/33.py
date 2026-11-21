"""
**Задача 33 (корреляции и ковариации).** Дана матрица характеристик формы `(365, 5)`. Вычислите:
- центрирование: `centered = data - data.mean(axis=0)`;
- ковариацию: `cov = centered.T @ centered / (365 - 1)`;
- стандартизацию: `standardized = centered / data.std(axis=0)`;
- корреляцию: `corr = standardized.T @ standardized / (365 - 1)`.

Проверьте, что `corr` симметрична и на диагонали единицы. Дополнительно: `np.corrcoef` для двух характеристик (например, мощность и расход). **Что продемонстрировать:** ковариацию и корреляцию через матричное умножение. **Вопросы:** чем ковариация отличается от корреляции; почему `centered.T @ centered` — матричное умножение; как broadcasting используется в центрировании; зачем стандартизация перед корреляцией.
"""
import numpy as np

rng = np.random.default_rng(33)
n = 365
power = rng.normal(150, 30, n)
data = np.column_stack([2e6 + 9000 * power + rng.normal(0, 3e5, n), power,
                        12 - 0.03 * power + rng.normal(0, 0.8, n), rng.normal(2.0, 0.5, n), rng.normal(1500, 200, n)])
centered = data - data.mean(axis=0)
cov = centered.T @ centered / (n - 1)
# ddof=1 в std, иначе (n-1) и std (делит на n) не согласованы и на диагонали получится n/(n-1), а не 1
standardized = centered / data.std(axis=0, ddof=1)
corr = standardized.T @ standardized / (n - 1)
print("cov совпадает с np.cov:", np.allclose(cov, np.cov(data, rowvar=False)))
print("corr симметрична:", np.allclose(corr, corr.T), "| диагональ:", np.diag(corr).round(6))
print("corr совпадает с np.corrcoef:", np.allclose(corr, np.corrcoef(data, rowvar=False)))
print("corrcoef(мощность, расход) =", np.corrcoef(data[:, 1], data[:, 2])[0, 1].round(3))
# Ковариация зависит от единиц измерения (рубли*лошадиные силы), корреляция безразмерна и
# лежит в [-1, 1]. centered.T @ centered - матричное умножение (5,n)@(n,5): элемент (i,j) =
# сумма по моделям произведений отклонений i-го и j-го признака = n-1 раз ковариация.
# Центрирование - broadcasting (n,5)-(5,). Стандартизация перед корреляцией приводит
# признаки к одному масштабу (std=1), поэтому матрица произведений = корреляции.

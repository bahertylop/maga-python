"""
**Задача 34 (линейная алгебра).** Дана система `A @ x = b`:
```python
A = np.array([[2.0, 1.0], [1.0, 3.0]])
b = np.array([5.0, 10.0])
```
Решите:
- `np.linalg.solve(A, b)`;
- `np.linalg.inv(A) @ b` — сравните.

Дополнительно: `np.linalg.det(A)`; `np.linalg.eig(A)`; `np.linalg.norm(b)`, `np.linalg.norm(b, ord=1)`, `np.linalg.norm(b, ord=np.inf)`. **Что продемонстрировать:** решение и все дополнительные функции. **Вопросы:** почему `solve` лучше `inv(A) @ b` (скорость, устойчивость, накопление ошибок); что такое собственные значения (пример: для диагональной — сами диагональные элементы); когда матрица не имеет обратной; как нормы используются для оценки сходства автомобилей (косинусное сходство характеристик).
"""
import numpy as np

A = np.array([[2.0, 1.0], [1.0, 3.0]])
b = np.array([5.0, 10.0])
x1 = np.linalg.solve(A, b)
x2 = np.linalg.inv(A) @ b
print("solve:", x1, "| inv@b:", x2, "| совпадают:", np.allclose(x1, x2))
print("det(A):", np.linalg.det(A))
vals, vecs = np.linalg.eig(A)
print("собственные значения:", vals.round(4), "\nвекторы:\n", vecs.round(4))
print("норма L2/L1/inf:", np.linalg.norm(b), np.linalg.norm(b, ord=1), np.linalg.norm(b, ord=np.inf))
# solve решает систему LU-разложением: быстрее (не строит всю обратную), устойчивее по
# ошибкам округления и точнее; inv(A) @ b считает лишнюю матрицу и накапливает погрешность.
# Собственные значения: A v = λ v (направления, которые матрица лишь растягивает);
# для диагональной матрицы λ - сами диагональные элементы.
print("eig диагональной:", np.linalg.eig(np.diag([3.0, 5.0]))[0])
# Обратной нет, когда det = 0 (строки линейно зависимы): linalg.inv бросит LinAlgError.
try:
    np.linalg.inv(np.array([[1.0, 2.0], [2.0, 4.0]]))
except np.linalg.LinAlgError as e:
    print("вырожденная ->", e)
# Нормы: косинусное сходство двух автомобилей по характеристикам u, v: (u·v)/(|u||v|)
u, v = np.array([150.0, 8.0, 2.0]), np.array([140.0, 9.0, 1.8])
print("cos-сходство:", round(float(u @ v / (np.linalg.norm(u) * np.linalg.norm(v))), 4))

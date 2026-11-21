"""
**Задача 30 (`unique` и операции над множествами).** Даны два массива марок от двух филиалов:
```python
branch1 = np.array(["Toyota", "BMW", "Kia", "Toyota", "Hyundai"])
branch2 = np.array(["BMW", "Kia", "Lada", "Toyota"])
```
Получите:
- уникальные марки каждого филиала;
- уникальные с количеством (`return_counts=True`);
- пересечение (`np.intersect1d`);
- объединение (`np.union1d`);
- разность (`np.setdiff1d`);
- симметричную разность (`np.setxor1d`);
- принадлежность (`np.isin`).

**Что продемонстрировать:** все операции. **Вопросы:** почему все операции возвращают отсортированные уникальные; чем `assume_unique=True` ускоряет; чем `np.isin` отличается от `np.in1d`; как работает `np.unique(..., axis=0)`.
"""
import numpy as np

branch1 = np.array(["Toyota", "BMW", "Kia", "Toyota", "Hyundai"])
branch2 = np.array(["BMW", "Kia", "Lada", "Toyota"])
print("уникальные 1:", np.unique(branch1), "| 2:", np.unique(branch2))
u, c = np.unique(branch1, return_counts=True)
print("с количеством:", dict(zip(u, c)))
print("пересечение  :", np.intersect1d(branch1, branch2))
print("объединение  :", np.union1d(branch1, branch2))
print("разность 1-2 :", np.setdiff1d(branch1, branch2))
print("симм. разн.  :", np.setxor1d(branch1, branch2))
print("isin         :", np.isin(branch1, branch2))
# Операции над множествами сначала приводят аргументы к УНИКАЛЬНЫМ значениям и возвращают
# их ОТСОРТИРОВАННЫМИ (реализация через сортировку). assume_unique=True говорит, что
# входы уже без повторов - NumPy пропускает unique и работает быстрее (если соврёте -
# результат неверный). np.isin - современная замена np.in1d (in1d устарел и удалён в
# новых версиях); isin сохраняет форму первого аргумента.
print("isin сохраняет форму:", np.isin(np.array([["BMW", "Lada"], ["Kia", "Audi"]]), branch2))
# unique(axis=0) - уникальные СТРОКИ матрицы (строки сравниваются целиком)
m = np.array([[1, 2], [3, 4], [1, 2]])
print("unique axis=0:\n", np.unique(m, axis=0))

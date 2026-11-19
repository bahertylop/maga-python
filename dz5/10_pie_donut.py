"""Задача 10. Pie chart и donut chart для кузовов."""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
if Path("sales.csv").exists():
    df = pd.read_csv("sales.csv")
    if "body_type" not in df: df["body_type"] = "Не указан"
    counts = df["body_type"].value_counts()
else:
    counts = pd.Series({"Седан": 32, "SUV": 28, "Хэтчбек": 18, "Купе": 10, "Универсал": 8, "Пикап": 4})
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), layout="constrained")
ax1.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 2})
ax1.set_title("Продажи по типу кузова")
ax2.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 2, "width": .4})
ax2.text(0, 0, f"Всего:\n{counts.sum():,}", ha="center", va="center")
ax2.set_title("Donut")
# autopct — формат процентов; %% в обычной строке printf-формата обозначает знак процента.
# startangle=90 начинает первый сектор сверху. explode смещает сектор наружу для акцента.
# Pie сложно читать при множестве (>~7) близких по размеру категорий — лучше bar.
# width в wedgeprops задаёт толщину кольца; центральная подпись помещается в отверстие.
# Pie не принимает отрицательные значения (ValueError). Возвраты отдельно анализируют,
# а для долей используют валовые продажи или абсолютные величины, не смешивая смысл метрики.
plt.show()

"""Задача 11. Экспорт PNG/PDF/SVG/JPEG, хэши, BytesIO."""
from pathlib import Path
from io import BytesIO
import hashlib, os
import matplotlib.pyplot as plt
output = Path("outputs")
output.mkdir(parents=True, exist_ok=True)  # Создаём папку заранее
fig, ax = plt.subplots(layout="constrained")
ax.plot([1, 2, 3, 4], [10, 15, 12, 20], marker="o")
ax.set(title="Отчёт автосалона", xlabel="Период", ylabel="Продажи")
files = [output / "report.png", output / "report.pdf", output / "report.svg",
         output / "report.jpg", output / "report_transparent.png"]
fig.savefig(files[0], dpi=300, bbox_inches="tight")
fig.savefig(files[1], metadata={"Title": "Отчёт автосалона", "Author": "Аналитика"})
fig.savefig(files[2])
fig.savefig(files[3], dpi=100, format="jpg")
fig.savefig(files[4], transparent=True)
for name in files:
    digest = hashlib.sha256(name.read_bytes()).hexdigest()[:8]
    print(name, "size:", os.path.getsize(name), "bytes; SHA-256:", digest)
buf = BytesIO()
fig.savefig(buf, format="png", dpi=150)
buf.seek(0)
print("BytesIO length:", len(buf.getvalue()))
# Хэш помогает сравнить версии, проверять артефакты CI и использовать кеширование.
# savefig до plt.close(fig), иначе закрытую/очищенную фигуру сохранить нельзя корректно.
# BytesIO хранит изображение в памяти; FastAPI: Response(content=buf.getvalue(), media_type='image/png').
# seek(0) возвращает указатель в начало при чтении через read(); getvalue() возвращает весь буфер.
# JPEG с потерями создаёт артефакты вокруг текста и тонких линий; для графиков лучше PNG/PDF/SVG.
# metadata задаёт метаданные формата (поддержка зависит от формата/backend).
# Если папки нет, savefig обычно FileNotFoundError; mkdir(parents=True, exist_ok=True) создаёт её.
plt.show()
plt.close(fig)

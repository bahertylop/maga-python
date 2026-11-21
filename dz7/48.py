"""
Задача 48 (экспорт: PdfPages, hashlib, логирование). Автосалон готовит ежемесячный отчёт: 12 графиков в PDF + отдельные PNG для email-рассылки. Реализуйте def export_all(fig, name, formats=("png", "pdf", "svg"), dpi=300, log_path=Path("export.log")): сохраните в outputs/{name}.{fmt}, залогируйте путь, размер и SHA-256 через logging. Дополнительно объедините все фигуры в report.pdf через with PdfPages("outputs/report.pdf") as pdf: for fig in figs: pdf.savefig(fig, bbox_inches="tight"). Ожидаемый вывод: 12+ файлов в outputs/; report.pdf объединяет все страницы; лог с хэшами. В комментариях объясните: зачем hashlib.sha256 (кэш CI — не пересобирать отчёт, если входные данные не менялись); как PdfPages работает как контекстный менеджер (наследует AbstractContextManager, автоматически закрывает файл); почему logging лучше print (уровни, форматирование, запись в файл); как закрыть фигуры (plt.close(fig) или plt.close("all") — избежать утечек памяти при 100+ графиков); как metadata={"Title": "Отчёт за январь", "Author": "Иванов"} встраивает информацию в PDF; почему Path удобнее os.path (кросс-платформенные пути, .mkdir(parents=True, exist_ok=True)).
"""
import hashlib
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

HERE = Path(__file__).parent
OUT = HERE / "outputs"
# Path: кросс-платформенные пути (оператор / вместо ручных разделителей), а mkdir с
# parents=True создаёт всю цепочку папок, exist_ok=True - не падает, если папка уже есть.
OUT.mkdir(parents=True, exist_ok=True)

# logging вместо print: уровни (DEBUG/INFO/ERROR), формат со временем, вывод одновременно в
# файл и консоль, можно включать/выключать без правки кода.
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                    handlers=[logging.FileHandler(OUT / "export.log", mode="w", encoding="utf-8"),
                              logging.StreamHandler()])
log = logging.getLogger("export")


def sha256_of(path: Path) -> str:
    # Читаем блоками: большой файл не загружается в память целиком.
    # Хэш = отпечаток содержимого: совпал -> файл не менялся -> CI может не пересобирать отчёт.
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def export_all(fig, name, formats=("png", "pdf", "svg"), dpi=300, out_dir=OUT):
    hashes = {}
    for fmt in formats:
        path = out_dir / f"{name}.{fmt}"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        hashes[fmt] = sha256_of(path)
        log.info("saved %s | %d bytes | sha256=%s", path.name, path.stat().st_size, hashes[fmt])
    return hashes


def make_fig(month):
    rng = np.random.default_rng(month)
    fig, ax = plt.subplots(figsize=(8, 4.5), layout="constrained")
    ax.plot(np.arange(1, 31), 40 + rng.normal(0, 5, 30).cumsum() / 3)
    ax.set(title=f"Продажи, месяц {month}", xlabel="День", ylabel="шт.")
    ax.grid(alpha=0.3)
    return fig


if __name__ == "__main__":
    figs = [make_fig(m) for m in range(1, 13)]
    for m, fig in enumerate(figs, start=1):
        export_all(fig, f"month_{m:02d}", formats=("png",), dpi=150)   # PNG для рассылки

    # PdfPages - контекстный менеджер: при выходе из with сам вызывает close() и
    # дописывает служебные структуры PDF (без close файл будет повреждён).
    # metadata встраивает свойства документа (видны в «Свойствах» PDF-ридера).
    with PdfPages(OUT / "report.pdf", metadata={"Title": "Отчёт за год", "Author": "Иванов"}) as pdf:
        for fig in figs:
            pdf.savefig(fig, bbox_inches="tight")
    log.info("report.pdf | pages=%d | sha256=%s", len(figs), sha256_of(OUT / "report.pdf"))

    # Закрываем фигуры: pyplot хранит ссылки на все открытые фигуры, и при 100+ графиках
    # память растёт (RuntimeWarning: More than 20 figures have been opened).
    for fig in figs:
        plt.close(fig)
    plt.close("all")
    print("Файлов в outputs/:", len(list(OUT.iterdir())))

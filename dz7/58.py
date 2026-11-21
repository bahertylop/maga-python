"""
Задача 58 (полный пайплайн: read_csv → groupby → savefig + PdfPages). Автосалон готовит отчёт автоматически: скрипт читает CSV, строит 4 графика, сохраняет в PDF и PNG, логирует хэши. Реализуйте def build_report(csv_path, out_dir): (1) df = pd.read_csv(csv_path, parse_dates=["date"], dtype={"cars_sold": "int32"}); (2) постройте 4 графика на одной фигуре (line по месяцам, barh по маркам, heatmap «марка × месяц», boxplot по моделям); (3) сохраните report.png (dpi=300) и report.pdf через PdfPages; (4) верните {"png": sha256, "pdf": sha256}. Ожидаемый вывод: файлы созданы; хэши возвращены. В комментариях объясните: как dtype="int32" экономит память (в 2 раза для целых); зачем parse_dates для корректных осей X (иначе строка, а не дата); как PdfPages объединяет многостраничный отчёт (with PdfPages(path) as pdf: pdf.savefig(fig)); зачем хэши (кэш CI — не пересобирать, если входные данные не менялись); как Path.mkdir(parents=True, exist_ok=True) создаёт папку (не падает, если существует); как логировать ошибки чтения (try/except FileNotFoundError).
"""
import hashlib
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

HERE = Path(__file__).parent
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("report")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def make_demo_csv(path: Path):
    rng = np.random.default_rng(58)
    brands = {"Toyota": ["Camry", "RAV4"], "Kia": ["Rio", "Sportage"], "BMW": ["X5", "3 Series"], "Hyundai": ["Solaris", "Creta"]}
    rows = [(d, b, m, int(rng.integers(3, 25)))
            for d in pd.date_range("2024-01-01", "2024-12-31", freq="3D") for b, ms in brands.items() for m in ms]
    pd.DataFrame(rows, columns=["date", "brand", "model", "cars_sold"]).to_csv(path, index=False)


def build_report(csv_path, out_dir):
    csv_path, out_dir = Path(csv_path), Path(out_dir)
    # mkdir(parents=True, exist_ok=True): создаёт всю цепочку папок и НЕ падает, если
    # папка уже существует (обычный mkdir бросил бы FileExistsError)
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        # parse_dates: без него date остаётся строкой -> ось X категориальная, нет
        # resample/диапазонов дат. dtype int32: 4 байта вместо 8 у int64 (в 2 раза экономнее).
        df = pd.read_csv(csv_path, parse_dates=["date"], dtype={"cars_sold": "int32"})
    except FileNotFoundError:
        log.error("Файл не найден: %s", csv_path)
        raise
    log.info("прочитано %d строк, cars_sold занимает %d байт", len(df), df["cars_sold"].memory_usage(index=False))

    monthly = df.groupby(df["date"].dt.to_period("M"))["cars_sold"].sum()
    by_brand = df.groupby("brand")["cars_sold"].sum().sort_values()
    heat = df.pivot_table(index="brand", columns=df["date"].dt.month, values="cars_sold", aggfunc="sum")
    models = [g["cars_sold"].values for _, g in df.groupby("model")]
    names = [m for m, _ in df.groupby("model")]

    fig, axes = plt.subplots(2, 2, figsize=(15, 10), layout="constrained")
    axes[0, 0].plot(monthly.index.to_timestamp(), monthly.values, marker="o")
    axes[0, 0].set_title("Продажи по месяцам")
    axes[0, 1].barh(by_brand.index, by_brand.values, color="C2")
    axes[0, 1].set_title("Продажи по маркам")
    im = axes[1, 0].imshow(heat.values, cmap="YlGnBu", aspect="auto")
    axes[1, 0].set_yticks(range(len(heat)), heat.index)
    axes[1, 0].set_xticks(range(heat.shape[1]), heat.columns)
    axes[1, 0].set_title("Марка × месяц")
    fig.colorbar(im, ax=axes[1, 0])
    axes[1, 1].boxplot(models, tick_labels=names)
    axes[1, 1].tick_params(axis="x", rotation=30)
    axes[1, 1].set_title("Распределение продаж по моделям")

    png, pdf_path = out_dir / "report.png", out_dir / "report.pdf"
    fig.savefig(png, dpi=300)
    with PdfPages(pdf_path) as pdf:             # контекстный менеджер: сам закроет файл
        pdf.savefig(fig)                        # страница 1 - общая сводка
        for ax_name, f in (("monthly", monthly),):
            fig2, ax2 = plt.subplots(figsize=(8, 4), layout="constrained")   # страница 2 - ещё график
            ax2.bar(range(len(f)), f.values)
            ax2.set_xticks(range(len(f)), [str(p) for p in f.index], rotation=45)
            pdf.savefig(fig2)
            plt.close(fig2)
    plt.close(fig)
    # Хэш SHA-256 - отпечаток содержимого: CI сравнивает хэши входных данных/результата и
    # не пересобирает отчёт, если ничего не изменилось
    return {"png": sha256_file(png), "pdf": sha256_file(pdf_path)}


if __name__ == "__main__":
    csv = HERE / "daily_sales_report.csv"
    make_demo_csv(csv)
    print(build_report(csv, HERE / "report_out"))
    try:
        build_report(HERE / "нет_такого.csv", HERE / "report_out")
    except FileNotFoundError:
        print("ошибка чтения залогирована, скрипт не упал молча")

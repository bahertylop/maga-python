"""
Задача 59 (полный бизнес-отчёт: 6 графиков + выводы). Автосалон готовит квартальный отчёт для совета директоров. Постройте фигуру 3×2: (0, 0) динамика продаж с rolling(30).mean(); (0, 1) barh по маркам (средняя цена); (1, 0) boxplot по моделям; (1, 1) scatter «мощность vs цена» с hue=body_type; (2, 0) heatmap «марка × месяц» из pivot_table; (2, 1) pie доли типов кузова (топ-5 + «Прочее»). Примените sns.set_theme(style="whitegrid") + setup_cyrillic(). Сохраните в quarterly_report.png (dpi=300) и quarterly_report.pdf. Сформулируйте 3–5 проверяемых рекомендаций с числами (например, «SUV растёт на 8% в месяц», «Toyota даёт 40% выручки»). Ожидаемый вывод: 6 графиков; рекомендации с числами; ограничения анализа. В комментариях объясните: как ax.axhline(mean, color="red", linestyle="--") аннотирует среднее; зачем barh для длинных названий марок; как pivot_table готовит heatmap (марка × месяц); как PlotConfig централизует настройки (все цвета/шрифты в одном месте); как проверить отсутствие отрицательных значений (assert (df["price"] >= 0).all()); какие ограничения анализа (сезонность, акции, выбросы).
"""
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import font_manager

HERE = Path(__file__).parent


@dataclass
class PlotConfig:
    """Все цвета/шрифты/размеры - в одном месте: меняем здесь, отчёт перестраивается целиком."""
    figsize: tuple = (16, 18)
    dpi: int = 300
    accent: str = "#0b5cad"
    mean_color: str = "red"
    fonts: tuple = ("DejaVu Sans", "Liberation Sans", "Arial", "sans-serif")


def setup_cyrillic(cfg: PlotConfig):
    have = {f.name for f in font_manager.fontManager.ttflist}
    fonts = [f for f in cfg.fonts if f in have or f == "sans-serif"]
    plt.rcParams.update({"font.family": fonts, "axes.unicode_minus": False, "font.size": 12})


def make_data(seed=59):
    rng = np.random.default_rng(seed)
    n = 3000
    brands = rng.choice(["Toyota", "Kia", "BMW", "Hyundai", "Volkswagen"], n, p=[0.35, 0.2, 0.1, 0.2, 0.15])
    base = {"Toyota": 2.4e6, "Kia": 1.9e6, "BMW": 5.0e6, "Hyundai": 2.0e6, "Volkswagen": 2.5e6}
    body = rng.choice(["SUV", "Седан", "Хэтчбек", "Универсал", "Купе", "Минивэн", "Пикап"], n,
                      p=[0.33, 0.25, 0.17, 0.08, 0.06, 0.06, 0.05])
    dates = pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 90, n), unit="D")
    boost = np.where(body == "SUV", 1.15, 1.0)
    power = rng.normal(150, 40, n).clip(70, 400)
    price = (np.array([base[b] for b in brands]) * boost + (power - 150) * 6000 + rng.normal(0, 2e5, n)).clip(4e5)
    return pd.DataFrame({"date": dates, "brand": brands, "model": [f"{b[:3]}-{k}" for b, k in zip(brands, rng.integers(1, 4, n))],
                         "body_type": body, "power": power, "price": price})


def main():
    cfg = PlotConfig()
    sns.set_theme(style="whitegrid")
    setup_cyrillic(cfg)                      # ПОСЛЕ set_theme: тема сбрасывает шрифты
    df = make_data()
    # Проверка данных до построения: цены не отрицательны (иначе график и выводы ложные)
    assert (df["price"] >= 0).all(), "найдены отрицательные цены"
    df["month"] = df["date"].dt.month
    daily = df.groupby("date").size().sort_index()

    fig, axes = plt.subplots(3, 2, figsize=cfg.figsize, layout="constrained")
    # (0,0) rolling(30).mean сглаживает шум; axhline(mean) - горизонталь среднего уровня
    ax = axes[0, 0]
    ax.plot(daily.index, daily.values, alpha=0.3, label="день")
    ax.plot(daily.index, daily.rolling(30, min_periods=1).mean(), color=cfg.accent, lw=2.5, label="скользящее 30")
    ax.axhline(daily.mean(), color=cfg.mean_color, linestyle="--", label=f"среднее {daily.mean():.1f}")
    ax.set_title("Динамика продаж"); ax.legend()
    # (0,1) barh: названия марок длинные - по горизонтали они читаются, не наезжая друг на друга
    avg_price = df.groupby("brand")["price"].mean().sort_values()
    axes[0, 1].barh(avg_price.index, avg_price.values, color=cfg.accent)
    axes[0, 1].set_title("Средняя цена по маркам")
    # (1,0) boxplot по моделям
    groups = [g["price"].values for _, g in df.groupby("model")]
    axes[1, 0].boxplot(groups, tick_labels=[m for m, _ in df.groupby("model")], patch_artist=True)
    axes[1, 0].tick_params(axis="x", rotation=60); axes[1, 0].set_title("Цены по моделям")
    # (1,1) scatter с hue
    sns.scatterplot(data=df.sample(600, random_state=1), x="power", y="price", hue="body_type", s=25, alpha=0.7, ax=axes[1, 1])
    axes[1, 1].set_title("Мощность vs цена")
    # (2,0) heatmap: pivot_table сворачивает «длинную» таблицу в матрицу марка×месяц
    heat = df.pivot_table(index="brand", columns="month", values="price", aggfunc="count")
    sns.heatmap(heat, annot=True, fmt="d", cmap="YlGnBu", ax=axes[2, 0])
    axes[2, 0].set_title("Продажи: марка × месяц")
    # (2,1) pie: топ-5 типов кузова + «Прочее»
    cnt = df["body_type"].value_counts()
    comb = pd.concat([cnt.head(5), pd.Series({"Прочее": cnt.iloc[5:].sum()})])
    axes[2, 1].pie(comb.values, labels=comb.index, autopct="%1.1f%%", wedgeprops={"edgecolor": "white"})
    axes[2, 1].set_title("Типы кузова")

    fig.suptitle("Квартальный отчёт автосалона", fontsize=20)
    fig.savefig(HERE / "quarterly_report.png", dpi=cfg.dpi)
    fig.savefig(HERE / "quarterly_report.pdf")
    plt.close(fig)

    # Рекомендации - ИЗ данных, с числами (каждую можно перепроверить)
    rev = (df.groupby("brand")["price"].sum() / df["price"].sum()).sort_values(ascending=False)
    monthly = df.groupby("month").size()
    suv_share = (df["body_type"] == "SUV").mean()
    corr = df["power"].corr(df["price"], method="spearman")
    recs = [
        f"1. {rev.index[0]} даёт {rev.iloc[0]:.0%} выручки квартала - держать приоритетным поставщиком.",
        f"2. SUV - {suv_share:.0%} продаж и самый частый тип кузова: наращивать складской запас.",
        f"3. Рост между первым и последним месяцем: {(monthly.iloc[-1] / monthly.iloc[0] - 1):+.0%} (проверить сезонность).",
        f"4. Спирмен(мощность, цена) = {corr:.2f}: мощность - сильный фактор цены, учитывать при акциях.",
    ]
    limits = ["сезонность: один квартал не показывает годового цикла;", "акции и скидки не учтены в цене;",
              "выбросы (дорогие редкие модели) смещают средние - смотреть медианы;", "данные синтетические - выводы демонстрационные."]
    text = "РЕКОМЕНДАЦИИ\n" + "\n".join(recs) + "\n\nОГРАНИЧЕНИЯ АНАЛИЗА\n" + "\n".join("- " + s for s in limits)
    (HERE / "quarterly_report_conclusions.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()

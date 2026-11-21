"""
Задача 60 (мини-проект: EDAPipeline — полный EDA + PdfPages + интерактивность). Финальный проект — собрать всё в классе EDAPipeline, который делает полный EDA датасета автосалона и выдаёт отчёт. Реализуйте class EDAPipeline с __init__(df, target=None), методами overview(ax) (scatter-пары), correlations(ax) (heatmap), distributions(ax) (violin), to_pdf(path) (статический PDF через PdfPages), to_png(path) (одна PNG-сводка), interactive() (RadioButtons-дашборд), report() (dict со summary). Загрузите данные автосалона (или Titanic), соберите полный отчёт: статические PNG + report.pdf + интерактивная фигура. Сформулируйте 5 инсайтов (например, «автомобили дороже 3 млн руб. имеют средний срок в шоу-руме менее 15 дней») и 3 рекомендации (например, «увеличить долю SUV — растут быстрее всех»). Ожидаемый вывод: PDF-отчёт, PNG, интерактив; инсайты с числами. В комментариях объясните: как PdfPages объединяет статические графики (одна страница на график); как отделить статику (to_pdf) от интерактива (interactive) — интерактив для презентации, статика для отчёта; зачем target в конструкторе (для supervised-задач — группировка по целевой переменной); как обрабатывать NaN (fillna/dropna перед визуализацией); какие графики не включать в отчёт (перегруженные, 3D-«для красоты», pie с >7 категориями); как проверить воспроизводимость (np.random.seed(42) перед каждой итерацией).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.widgets import RadioButtons

HERE = Path(__file__).parent


def make_showroom(seed=42):
    # Воспроизводимость: фиксируем seed перед генерацией (и перед каждым запуском
    # пайплайна) - тогда отчёт и инсайты идентичны между прогонами
    rng = np.random.default_rng(seed)
    n = 1500
    body = rng.choice(["SUV", "Седан", "Хэтчбек", "Купе"], n, p=[0.4, 0.3, 0.2, 0.1])
    power = rng.normal(150, 40, n).clip(70, 400)
    age = rng.integers(0, 15, n)
    price = (1.2e6 + power * 9000 - age * 90_000 + np.where(body == "SUV", 3e5, 0) + rng.normal(0, 2.5e5, n)).clip(4e5)
    days = (10 + price / 2e5 + rng.normal(0, 4, n)).clip(1)
    df = pd.DataFrame({"price": price, "power": power, "car_age": age, "days_in_showroom": days, "body_type": body})
    df.loc[rng.choice(n, 30, replace=False), "days_in_showroom"] = np.nan     # пропуски
    return df


class EDAPipeline:
    def __init__(self, df: pd.DataFrame, target: str = None):
        # NaN: dropna убирает строки с пропусками (если их мало), fillna(median) сохраняет
        # объём данных. Здесь заполняем медианой ЧИСЛОВЫЕ столбцы - до визуализации,
        # иначе hist/violin/corr молча игнорируют NaN или считают по разным подвыборкам.
        self.df = df.copy()
        num = self.df.select_dtypes("number").columns
        self.df[num] = self.df[num].fillna(self.df[num].median())
        # target нужен для supervised-задач: корреляции с целью, разбивка по классам/значению
        self.target = target
        self.num = list(num)

    def overview(self, ax):
        cols = [c for c in self.num if c != self.target][:1] or self.num[:1]
        s = self.df.sample(min(600, len(self.df)), random_state=0)
        ax.scatter(s[cols[0]], s[self.target or self.num[0]], alpha=0.4, s=12)
        ax.set(xlabel=cols[0], ylabel=self.target, title=f"{cols[0]} vs {self.target}")

    def correlations(self, ax):
        corr = self.df[self.num].corr(method="spearman")
        im = ax.imshow(corr, cmap="RdBu", vmin=-1, vmax=1)
        ax.set_xticks(range(len(corr)), corr.columns, rotation=45, ha="right")
        ax.set_yticks(range(len(corr)), corr.index)
        for i in range(len(corr)):
            for j in range(len(corr)):
                ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8)
        ax.figure.colorbar(im, ax=ax)
        ax.set_title("Корреляции Спирмена")

    def distributions(self, ax):
        groups = [g[self.target or self.num[0]].values for _, g in self.df.groupby("body_type")]
        ax.violinplot(groups, showmedians=True)
        ax.set_xticks(range(1, len(groups) + 1), sorted(self.df["body_type"].unique()))
        ax.set_title(f"Распределение {self.target} по типам кузова")

    def _panels(self):
        return [self.overview, self.correlations, self.distributions]

    def to_pdf(self, path):
        # PdfPages: каждый pdf.savefig(fig) = ОДНА страница; все графики - в одном файле.
        # Статика (PDF/PNG) - для отчёта: воспроизводимая, без виджетов.
        with PdfPages(path) as pdf:
            for panel in self._panels():
                fig, ax = plt.subplots(figsize=(8, 6), layout="constrained")
                panel(ax)
                pdf.savefig(fig)
                plt.close(fig)
        return Path(path)

    def to_png(self, path):
        fig, axes = plt.subplots(1, 3, figsize=(20, 6), layout="constrained")
        for panel, ax in zip(self._panels(), axes):
            panel(ax)
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return Path(path)

    def interactive(self):
        # Интерактив - для ПРЕЗЕНТАЦИИ (живое переключение), не для отчёта: его нельзя
        # вложить в PDF. Виджеты храним в атрибутах (иначе их удалит сборщик мусора).
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.subplots_adjust(left=0.25)
        self._radio = RadioButtons(fig.add_axes([0.02, 0.4, 0.18, 0.3]), self.num)

        def draw(feature):
            ax.cla()
            ax.hist(self.df[feature], bins=25)
            ax.set_title(feature)
            fig.canvas.draw_idle()

        self._radio.on_clicked(draw)
        draw(self.num[0])
        return fig

    def report(self):
        d = self.df
        expensive = d[d["price"] > 3e6]
        corr_t = d[self.num].corr(method="spearman")[self.target].drop(self.target).sort_values(key=abs, ascending=False)
        suv_premium = d[d["body_type"] == "SUV"]["price"].median() / d[d["body_type"] != "SUV"]["price"].median() - 1
        return {
            "rows": len(d), "target": self.target,
            "median_price": d["price"].median(),
            "share_expensive": len(expensive) / len(d),
            "days_expensive": expensive["days_in_showroom"].mean(),
            "days_cheap": d[d["price"] <= 3e6]["days_in_showroom"].mean(),
            "top_corr": corr_t.index[0], "top_corr_value": corr_t.iloc[0],
            "suv_share": (d["body_type"] == "SUV").mean(), "suv_premium": suv_premium,
            "age_effect_per_year": np.polyfit(d["car_age"], d["price"], 1)[0],
        }


if __name__ == "__main__":
    eda = EDAPipeline(make_showroom(42), target="price")
    eda.to_png(HERE / "60_summary.png")
    eda.to_pdf(HERE / "60_report.pdf")
    fig = eda.interactive()
    eda._radio.set_active(1)                      # имитация клика
    fig.savefig(HERE / "60_interactive.png", dpi=120)
    r = eda.report()
    print("5 ИНСАЙТОВ")
    print(f"1. Дороже 3 млн: {r['share_expensive']:.0%} машин; в шоу-руме {r['days_expensive']:.0f} дн. против {r['days_cheap']:.0f} дн. у остальных.")
    print(f"2. Сильнее всего с ценой связана «{r['top_corr']}» (Спирмен {r['top_corr_value']:+.2f}).")
    print(f"3. Каждый год возраста снижает цену на {abs(r['age_effect_per_year']):,.0f} руб.")
    print(f"4. SUV - {r['suv_share']:.0%} предложения; их медианная цена выше на {r['suv_premium']:.0%}.")
    print(f"5. Медианная цена: {r['median_price']:,.0f} руб. по {r['rows']} автомобилям.")
    print("3 РЕКОМЕНДАЦИИ\n1. Увеличить долю SUV - спрос и маржа выше.\n2. Для машин дороже 3 млн пересмотреть цену, если срок > 15 дн.\n3. Закупать авто моложе - каждый год старения теряет значимую часть цены.")

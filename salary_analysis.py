"""Расчёты и галерея графиков по учебному датасету вакансий.

Запуск: python salary_analysis.py vacancies.csv --output .
Исходные строки не включены в репозиторий. Графики строятся из переданного CSV.
"""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, PercentFormatter
from matplotlib.patches import FancyBboxPatch
from scipy.stats import gaussian_kde, mannwhitneyu

ORDER = ["Нет опыта", "От 1 года до 3 лет", "От 3 до 6 лет", "Более 6 лет"]
SHORT = ["Нет опыта", "1–3 года", "3–6 лет", "Более 6 лет"]
INK, GREY, LIGHT, BLUE = "#141414", "#707070", "#ececec", "#2965a3"
COLORS = ["#2965a3", "#278276", "#aa7035", "#7d609e"]


def read_data(path):
    df = pd.read_csv(path)
    required = {"vacancy_id", "salary_from", "salary_to", "experience", "city"}
    if not required.issubset(df.columns):
        raise ValueError(f"Нет столбцов: {sorted(required - set(df.columns))}")
    if not df.vacancy_id.is_unique:
        raise ValueError("Идентификаторы вакансий повторяются")
    unknown = set(df.experience.dropna()) - set(ORDER)
    if unknown or df.experience.isna().any():
        raise ValueError(f"Неизвестные или пустые категории опыта: {unknown}")
    for col in ["salary_from", "salary_to"]:
        df[col] = pd.to_numeric(df[col], errors="raise")
        known = df[col].dropna()
        if (known <= 0).any() or not np.isfinite(known).all():
            raise ValueError("Указанные зарплаты должны быть положительными и конечными")
    # При двух границах — середина вилки; при одной — указанная граница.
    df["salary"] = df[["salary_from", "salary_to"]].mean(axis=1)
    df["inverted"] = df.salary_from.notna() & df.salary_to.notna() & (df.salary_from > df.salary_to)
    return df


def summarize(df):
    records = []
    for group, label in zip(ORDER, SHORT):
        s = df.loc[df.experience.eq(group), "salary"].dropna()
        if len(s) < 2:
            raise ValueError(f"Недостаточно значений: {group}")
        records.append(dict(experience=label, count=len(s), mean_rub=s.mean(),
                            median_rub=s.median(), q25_rub=s.quantile(.25),
                            q75_rub=s.quantile(.75), sd_rub=s.std(), skewness=s.skew()))
    return pd.DataFrame(records)


def canvas(title, subtitle, size=(10.8, 6.5)):
    fig, ax = plt.subplots(figsize=size)
    fig.subplots_adjust(left=.16, right=.96, bottom=.16, top=.78)
    fig.text(.06, .94, title, fontsize=20, weight="bold", va="top")
    fig.text(.06, .875, subtitle, fontsize=10, color=GREY, va="top")
    return fig, ax


def clean(ax, grid="x"):
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0, pad=9)
    ax.set_axisbelow(True)
    if grid:
        ax.grid(axis=grid, color=LIGHT)


def save(fig, root, name, note):
    fig.text(.06, .035, note, fontsize=9, color=GREY, va="bottom")
    fig.savefig(root / f"{name}.png", dpi=160, facecolor="white")
    fig.savefig(root / f"{name}.svg", facecolor="white")
    plt.close(fig)


def draw_gallery(df, summary, root):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "text.color": INK, "axes.labelcolor": INK,
                         "xtick.color": GREY, "ytick.color": INK,
                         "svg.fonttype": "none"})
    mean, med = summary.mean_rub.to_numpy()/1000, summary.median_rub.to_numpy()/1000
    q1, q3 = summary.q25_rub.to_numpy()/1000, summary.q75_rub.to_numpy()/1000
    y = np.arange(4)
    fig, ax = canvas("Среднее и медиана", "Группированные столбцы · одинаковая шкала для двух показателей")
    ax.barh(y+.17, mean, height=.28, color=GREY, label="Среднее")
    ax.barh(y-.17, med, height=.28, color=BLUE, label="Медиана")
    for j in y:
        ax.text(mean[j]+14, j+.17, f"{mean[j]:.0f}", va="center", fontsize=10)
        ax.text(med[j]+14, j-.17, f"{med[j]:.0f}", va="center", fontsize=10, color=BLUE)
    ax.set(yticks=y, yticklabels=SHORT, xlabel="тыс. ₽", xlim=(0,1100))
    ax.invert_yaxis(); clean(ax); ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0,1.12), ncol=2)
    save(fig, root, "salary-means-bars", "74 410 вакансий с зарплатой. Значения округлены только в подписях.")

    fig, ax = canvas("Разрыв между средним и медианой", "Dumbbell plot · соединённые точки показывают разницу")
    ax.hlines(y, med, mean, color="#c9c9c9", lw=4)
    ax.scatter(mean,y,s=75,color=GREY,label="Среднее",zorder=3)
    ax.scatter(med,y,s=75,color=BLUE,label="Медиана",zorder=3)
    for j in y:
        ax.text((mean[j]+med[j])/2,j-.14,f"× {mean[j]/med[j]:.2f}",ha="center",fontsize=11)
    ax.set(yticks=y, yticklabels=SHORT, xlabel="тыс. ₽", xlim=(0,1050), ylim=(3.55,-.6))
    clean(ax); ax.legend(frameon=False,loc="upper left",bbox_to_anchor=(0,1.12),ncol=2)
    save(fig,root,"salary-means-dumbbell","Коэффициент над линией — среднее / медиана, а не темп роста зарплаты.")

    fig, ax = canvas("Четыре группы — четыре сравнения", "Авторская компоновка · карточки с числами и общей шкалой", size=(10.8,7))
    ax.set_axis_off(); ax.set(xlim=(0,1),ylim=(0,1))
    for j in y:
        x=.02+(j%2)*.50; yy=.58-(j//2)*.50
        ax.add_patch(FancyBboxPatch((x,yy-.05),.45,.43,boxstyle="round,pad=0.012",facecolor="white",edgecolor="#cccccc"))
        ax.text(x+.03,yy+.30,SHORT[j],weight="bold",fontsize=13)
        ax.text(x+.03,yy+.21,f"Медиана {med[j]:.0f} тыс. ₽",fontsize=13,color=BLUE)
        ax.text(x+.03,yy+.14,f"Среднее {mean[j]:.0f} тыс. ₽",fontsize=11,color=GREY)
        for k,(value,color) in enumerate([(mean[j],GREY),(med[j],BLUE)]):
            ax.plot([x+.03,x+.40],[yy+.07-k*.045]*2,color=LIGHT,lw=7,solid_capstyle="butt")
            ax.plot([x+.03,x+.03+.37*value/1000],[yy+.07-k*.045]*2,color=color,lw=7,solid_capstyle="butt")
        ax.text(x+.03,yy-.018,f"Разница {mean[j]-med[j]:.0f} тыс. ₽  ·  × {mean[j]/med[j]:.2f}",fontsize=9)
    save(fig,root,"salary-means-cards","Длина полос во всех карточках рассчитана по одной шкале: 0–1 000 тыс. ₽.")

    fig,ax=canvas("Центральные 50% зарплат", "Интервальная диаграмма · от 25-го до 75-го перцентиля")
    ax.hlines(y,q1,q3,color=BLUE,lw=9)
    ax.scatter(med,y,s=75,color=INK,edgecolor="white",zorder=3)
    for j in y:
        ax.text(q1[j]-7,j,f"{q1[j]:g}",ha="right",va="center",fontsize=10)
        ax.text(q3[j]+7,j,f"{q3[j]:g}",ha="left",va="center",fontsize=10)
        ax.text(med[j],j-.22,f"медиана {med[j]:g}",ha="center",fontsize=10)
    ax.set(yticks=y,yticklabels=SHORT,xlabel="тыс. ₽",xlim=(0,470),ylim=(3.6,-.65));clean(ax)
    save(fig,root,"salary-quartiles-interval","Отрезки — межквартильные диапазоны, а не доверительные интервалы.")

    arrays=[df.loc[df.experience.eq(g),"salary"].dropna().to_numpy()/1000 for g in ORDER]
    fig,ax=canvas("Распределения по опыту", "Boxplot по исходным строкам · выбросы скрыты только на рисунке")
    box=ax.boxplot(arrays,orientation="horizontal",patch_artist=True,showfliers=False,whis=1.5,
                   tick_labels=SHORT,medianprops={"color":INK,"linewidth":2},widths=.5)
    for patch,color in zip(box["boxes"],COLORS): patch.set(facecolor=color,alpha=.35)
    ax.set(xlabel="тыс. ₽",xlim=(0,700));ax.invert_yaxis();clean(ax)
    save(fig,root,"salary-quartiles-boxplot","Ящик — Q1–Q3; усы — крайние наблюдения в пределах 1,5 IQR. Все строки остаются в расчётах.")

    fig,ax=canvas("Диапазон относительно медианы", "Авторская нормировка · медиана каждой группы принята за 100%")
    ax.axvline(100,color=INK,lw=1,ls="--")
    ax.hlines(y,100*q1/med,100*q3/med,color=BLUE,lw=12)
    ax.scatter(np.full(4,100),y,s=70,color=INK,zorder=3)
    for j in y: ax.text(100*q3[j]/med[j]+3,j,f"IQR / медиана: {100*(q3[j]-q1[j])/med[j]:.1f}%",va="center",fontsize=10)
    ax.set(yticks=y,yticklabels=SHORT,xlabel="% от медианы своей группы",xlim=(40,250),ylim=(3.6,-.6));clean(ax)
    save(fig,root,"salary-quartiles-normalized","Для сравнения относительного разброса. Различия абсолютных зарплат здесь не показаны.")

    city=df.loc[df.experience.eq(ORDER[1])].groupby("city").salary.agg(["count","median"]).dropna().sort_values("median",ascending=False)
    labels=list(city.index); values=city["median"].to_numpy()/1000; cy=np.arange(len(city))
    fig,ax=canvas("Медианы зарплат по городам", "Столбчатая диаграмма · только вакансии с опытом 1–3 года")
    ax.barh(cy,values,color=BLUE,height=.6)
    for j,v in enumerate(values): ax.text(v+3,j,f"{v:g}",va="center",fontsize=11)
    ax.set(yticks=cy,yticklabels=labels,xlabel="тыс. ₽",xlim=(0,200));ax.invert_yaxis();clean(ax)
    save(fig,root,"salary-cities-bars","Различия городов также могут отражать состав вакансий. Период выгрузки не подтверждён.")

    fig,ax=canvas("Города относительно общей медианы", "Lollipop plot · вертикальная линия — 150 тыс. ₽ для всей группы 1–3 года")
    ax.hlines(cy,0,values,color="#c9c9c9",lw=2);ax.scatter(values,cy,s=90,color=BLUE,zorder=3)
    ax.axvline(150,color=INK,ls="--",lw=1)
    for j,v in enumerate(values): ax.text(v+3,j,f"{v:g}  ·  n={city['count'].iloc[j]:,}".replace(","," "),va="center",fontsize=10)
    ax.set(yticks=cy,yticklabels=labels,xlabel="тыс. ₽",xlim=(0,230));ax.invert_yaxis();clean(ax)
    save(fig,root,"salary-cities-lollipop","Число вакансий указано рядом с медианой. Сравнивается одна категория требуемого опыта.")

    matrix=df.pivot_table(index="city",columns="experience",values="salary",aggfunc="median").reindex(index=labels,columns=ORDER)/1000
    fig,ax=canvas("Город × требуемый опыт", "Матрица медиан · дополнительная сегментация той же выборки")
    im=ax.imshow(matrix,cmap="Blues",aspect="auto",vmin=0,vmax=matrix.max().max())
    for r in range(len(labels)):
        for c in range(4):
            value=matrix.iloc[r,c]
            ax.text(c,r,f"{value:g}",ha="center",va="center",color="white" if value>matrix.max().max()*.6 else INK)
    ax.set(xticks=range(4),xticklabels=SHORT,yticks=range(len(labels)),yticklabels=labels)
    fig.colorbar(im,ax=ax,shrink=.75,pad=.025,label="тыс. ₽");clean(ax,None)
    save(fig,root,"salary-cities-matrix","Каждая ячейка — отдельная медиана по исходным строкам. Численности сегментов: city-counts.csv.")

    for logarithmic,name in [(False,"salary-distribution-histogram"),(True,"salary-distribution-loghist")]:
        fig,axs=plt.subplots(2,2,figsize=(10.8,8.2),sharex=True,sharey=True)
        fig.subplots_adjust(left=.1,right=.96,bottom=.15,top=.81,hspace=.38)
        fig.text(.06,.95,"Полное распределение" if logarithmic else "Основная часть распределения",fontsize=20,weight="bold",va="top")
        fig.text(.06,.89,"Гистограммы · логарифмические интервалы" if logarithmic else "Гистограммы · одинаковые интервалы по 25 тыс. ₽",fontsize=10,color=GREY)
        bins=np.logspace(np.log10(df.salary.min()/1000),np.log10(df.salary.max()/1000)+1e-8,48) if logarithmic else np.arange(0,1025,25)
        for ax,s,label,color in zip(axs.flat,arrays,SHORT,COLORS):
            ax.hist(s,bins=bins,weights=np.full(len(s),1/len(s)),color=color,edgecolor="white",lw=.35)
            ax.axvline(np.median(s),color=INK,ls="--",lw=1)
            ax.set_title(label,loc="left",fontsize=12)
            ax.text(.98,.91,f"n={len(s):,}".replace(","," ")+ ("" if logarithmic else f"\nВыше 1 млн: {np.mean(s>1000):.2%}"),transform=ax.transAxes,ha="right",va="top",fontsize=9)
            if logarithmic:
                ax.set_xscale("log");ax.set_xticks([10,100,1000,10000],["10","100","1 000","10 000"])
            else: ax.set_xlim(0,1000)
            ax.yaxis.set_major_formatter(PercentFormatter(1,0));clean(ax,"y")
        for ax in axs[-1]: ax.set_xlabel("тыс. ₽ · логарифмическая ось" if logarithmic else "тыс. ₽")
        for ax in axs[:,0]: ax.set_ylabel("Доля вакансий группы")
        save(fig,root,name,"Пунктир — медиана. Доли считаются от всех вакансий группы с зарплатой; экстремальные значения не удалены.")

    fig,ax=canvas("Какая доля вакансий ниже порога", "ECDF · эмпирическое накопленное распределение без выбора ширины интервалов")
    for s,label,color in zip(arrays,SHORT,COLORS):
        sorted_s=np.sort(s);ax.step(sorted_s,np.arange(1,len(s)+1)/len(s),where="post",color=color,label=label,lw=2)
    ax.set_xscale("log");ax.set_xticks([10,100,1000,10000],["10","100","1 000","10 000"])
    ax.set(xlabel="тыс. ₽ · логарифмическая ось",ylabel="Доля вакансий с зарплатой ≤ порога",ylim=(0,1.05))
    ax.yaxis.set_major_formatter(PercentFormatter(1));clean(ax,"y");ax.legend(frameon=False,loc="center right")
    save(fig,root,"salary-distribution-ecdf","Все наблюдения включены. 50% на вертикальной оси соответствует медиане.")

    fig,ax=canvas("Форма распределений на одной шкале", "Violin plot · плотность оценена в логарифмах зарплаты, все наблюдения включены")
    log_arrays=[np.log10(s) for s in arrays]
    violins=ax.violinplot(log_arrays,positions=np.arange(4),orientation="horizontal",showmedians=True,showextrema=False,widths=.7)
    for body,color in zip(violins["bodies"],COLORS): body.set_facecolor(color);body.set_alpha(.45)
    violins["cmedians"].set_color(INK)
    ax.set(yticks=range(4),yticklabels=SHORT,xticks=[1,2,3,4],xticklabels=["10","100","1 000","10 000"],xlabel="тыс. ₽ · логарифмическая ось")
    ax.invert_yaxis();clean(ax)
    save(fig,root,"salary-distribution-violin","Ширина показывает сглаженную плотность в log10(тыс. ₽), а не число вакансий. Чёрная линия — медиана.")

    # Дополнительная авторская форма: KDE с одинаковой высотой для каждого профиля.
    fig,ax=canvas("Профили зарплат", "Авторская компоновка · четыре полосы плотности на общей логарифмической шкале")
    grid=np.linspace(min(s.min() for s in log_arrays),max(s.max() for s in log_arrays),450)
    for j,(s,label,color) in enumerate(zip(log_arrays,SHORT,COLORS)):
        density=gaussian_kde(s)(grid);density=.62*density/density.max()
        ax.fill_between(grid,3-j,3-j+density,color=color,alpha=.45)
        ax.plot(grid,3-j+density,color=color,lw=1.3)
        ax.plot([np.median(s)]*2,[3-j,3-j+.55],color=INK,lw=1)
    ax.set(yticks=range(4),yticklabels=SHORT[::-1],xticks=[1,2,3,4],xticklabels=["10","100","1 000","10 000"],xlabel="тыс. ₽ · логарифмическая ось",ylim=(-.12,3.9))
    clean(ax,None)
    save(fig,root,"salary-distribution-ridgeline","Каждый профиль нормирован по своему максимуму. Высота не сравнивает численности групп; линии — медианы.")

    quality=df.groupby("experience").salary.agg(["size","count"]).reindex(ORDER)
    missing=100*(quality["size"]-quality["count"])/quality["size"]
    fig,ax=canvas("Где зарплата указана реже", "100% stacked bars · полнота данных в каждой категории опыта")
    ax.barh(y,100-missing,color=BLUE,label="Зарплата указана",height=.55)
    ax.barh(y,missing,left=100-missing,color=LIGHT,label="Не указана",height=.55)
    for j in y: ax.text(101,j,f"Нет данных: {missing.iloc[j]:.1f}%",va="center",fontsize=10)
    ax.set(yticks=y,yticklabels=SHORT,xlabel="% всех вакансий группы",xlim=(0,138));ax.invert_yaxis();clean(ax,None)
    ax.legend(frameon=False,loc="upper left",bbox_to_anchor=(0,1.12),ncol=2)
    save(fig,root,"salary-quality-missing","100 000 исходных строк; 25 590 без зарплаты. Пропуски различаются между категориями опыта.")

    fig,ax=canvas("Доля вакансий без зарплаты", "Dot plot · акцент на пропусках вместо заполненной части")
    ax.hlines(y,0,missing,color="#c9c9c9",lw=2)
    ax.scatter(missing,y,s=100,color=INK,zorder=3)
    for j in y: ax.text(missing.iloc[j]+2,j,f"{missing.iloc[j]:.1f}%",va="center")
    ax.set(yticks=y,yticklabels=SHORT,xlabel="% всех вакансий группы",xlim=(0,100));ax.invert_yaxis();clean(ax)
    save(fig,root,"salary-quality-dots","Знаменатель — все вакансии своей категории, включая строки без зарплаты.")

    fig,ax=canvas("Полнота данных: доля и объём", "Авторская компоновка · карточки дополняют проценты числом строк",size=(10.8,7))
    ax.set_axis_off();ax.set(xlim=(0,1),ylim=(0,1))
    for j in y:
        x=.02+(j%2)*.50; yy=.58-(j//2)*.50
        ax.add_patch(FancyBboxPatch((x,yy-.05),.45,.43,boxstyle="round,pad=0.012",facecolor="white",edgecolor="#cccccc"))
        total=int(quality['size'].iloc[j]); known=int(quality['count'].iloc[j]); absent=total-known
        ax.text(x+.03,yy+.30,SHORT[j],weight="bold",fontsize=13)
        ax.text(x+.03,yy+.21,f"Без зарплаты {missing.iloc[j]:.1f}%",fontsize=13)
        ax.text(x+.03,yy+.13,f"{absent:,} из {total:,} строк".replace(","," "),fontsize=11,color=GREY)
        ax.plot([x+.03,x+.40],[yy+.055]*2,color=LIGHT,lw=9,solid_capstyle="butt")
        ax.plot([x+.03,x+.03+.37*missing.iloc[j]/100],[yy+.055]*2,color=INK,lw=9,solid_capstyle="butt")
        ax.text(x+.03,yy-.018,f"С зарплатой: {known:,}".replace(","," "),fontsize=10,color=BLUE)
    save(fig,root,"salary-quality-cards","Шкала полос во всех карточках — 0–100%. Числа позволяют оценить объём доступных данных.")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv",type=Path)
    parser.add_argument("--output",type=Path,default=Path(__file__).parent)
    args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    df=read_data(args.csv); summary=summarize(df)
    summary.to_csv(args.output/"salary-summary.csv",index=False)
    complete=df.salary_from.notna() & df.salary_to.notna()
    variants={"Все указанные зарплаты":df, "Без обратных вилок":df.loc[~df.inverted],
              "Только полные вилки":df.loc[complete], "До 1 млн, диагностика":df.loc[df.salary.le(1_000_000)]}
    sensitivity=pd.concat([summarize(frame).assign(method=label) for label,frame in variants.items()],ignore_index=True)
    sensitivity.to_csv(args.output/"sensitivity-summary.csv",index=False)
    cities=df.loc[df.experience.eq(ORDER[1])].groupby("city").salary.agg(["count","median"])
    cities.rename(columns={"median":"median_rub"}).to_csv(args.output/"city-medians.csv")
    df.pivot_table(index="city",columns="experience",values="salary",aggfunc="count").reindex(columns=ORDER).to_csv(args.output/"city-counts.csv")
    df.groupby("experience").salary.agg(["size","count"]).reindex(ORDER).to_csv(args.output/"data-quality.csv")
    x=df.loc[df.experience.eq(ORDER[2]),"salary"].dropna()
    y=df.loc[df.experience.eq(ORDER[1]),"salary"].dropna()
    u=mannwhitneyu(x,y,alternative="greater",method="asymptotic")
    meta=dict(rows=len(df),salary_rows=int(df.salary.notna().sum()),missing_salary_rows=int(df.salary.isna().sum()),
              inverted_ranges=int(df.inverted.sum()),sha256=hashlib.sha256(args.csv.read_bytes()).hexdigest(),
              mann_whitney=dict(U=float(u.statistic),p=float(u.pvalue),rank_biserial=float(2*u.statistic/(len(x)*len(y))-1)))
    (args.output/"analysis-checks.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
    draw_gallery(df,summary,args.output)
    print(json.dumps(meta,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()

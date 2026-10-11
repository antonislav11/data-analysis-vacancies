# Варианты визуализации зарплат

17 графиков по одному исходному датасету. PNG — для просмотра; SVG — для масштабирования.

[← К разбору проекта](README.md) · [Последние расчёты](generated/REPORT.md)

## Среднее и медиана

Среднее выше медианы в 2,90–3,55 раза. Я использую медиану вместе с квартилями, чтобы описать типичное предложение; среднее оставляю для анализа влияния хвоста.

### Среднее и медиана

Основной вариант.

![Среднее и медиана](generated/salary-means-bars.png)

[PNG](generated/salary-means-bars.png) · [SVG](generated/salary-means-bars.svg)

### Соединённые точки, dumbbell

Удобно сравнить разрыв между двумя показателями.

![Соединённые точки, dumbbell](generated/salary-means-dumbbell.png)

[PNG](generated/salary-means-dumbbell.png) · [SVG](generated/salary-means-dumbbell.svg)

### Авторские карточки

Подходят для короткого обзора; полосы имеют общую шкалу.

![Авторские карточки](generated/salary-means-cards.png)

[PNG](generated/salary-means-cards.png) · [SVG](generated/salary-means-cards.svg)

## Разброс и центральный диапазон

Самый широкий абсолютный IQR — 165 тыс. ₽ в группе более 6 лет. Самый большой IQR относительно медианы — 71,7% в группе 1–3 года. Интервалы Q1–Q3 содержат центральные 50% наблюдений; это не доверительные интервалы.

### Разброс и центральный диапазон

Основной вариант.

![Разброс и центральный диапазон](generated/salary-quartiles-interval.png)

[PNG](generated/salary-quartiles-interval.png) · [SVG](generated/salary-quartiles-interval.svg)

### Boxplot по исходным строкам

Показывает квартили, медиану и усы по правилу 1,5 IQR; выбросы скрыты только на рисунке.

![Boxplot по исходным строкам](generated/salary-quartiles-boxplot.png)

[PNG](generated/salary-quartiles-boxplot.png) · [SVG](generated/salary-quartiles-boxplot.svg)

### Авторская нормировка относительно медианы

Позволяет сравнить относительный разброс групп с разным уровнем зарплаты.

![Авторская нормировка относительно медианы](generated/salary-quartiles-normalized.png)

[PNG](generated/salary-quartiles-normalized.png) · [SVG](generated/salary-quartiles-normalized.svg)

## Сравнение городов

В группе 1–3 года медиана меняется от 95 тыс. ₽ в Нижнем Новгороде до 167,5 тыс. ₽ в Москве. Категорию опыта я фиксирую, чтобы сравнение городов было точнее. Состав профессий и тип занятости всё ещё могут влиять на разницу.

### Сравнение городов

Основной вариант.

![Сравнение городов](generated/salary-cities-bars.png)

[PNG](generated/salary-cities-bars.png) · [SVG](generated/salary-cities-bars.svg)

### Точки и ориентир, lollipop

Сопоставляет города с медианой всей группы и показывает размер каждого сегмента.

![Точки и ориентир, lollipop](generated/salary-cities-lollipop.png)

[PNG](generated/salary-cities-lollipop.png) · [SVG](generated/salary-cities-lollipop.svg)

### Матрица город × опыт

Добавляет второй разрез: медианы всех четырёх категорий опыта.

![Матрица город × опыт](generated/salary-cities-matrix.png)

[PNG](generated/salary-cities-matrix.png) · [SVG](generated/salary-cities-matrix.svg)

## Форма распределений

На линейной гистограмме показана часть до 1 млн ₽, но доли рассчитаны от всей группы, а значения за пределами подписаны. Остальные варианты охватывают все наблюдения. Распределения строю по отдельным строкам вакансий.

### Форма распределений

Основной вариант.

![Форма распределений](generated/salary-distribution-histogram.png)

[PNG](generated/salary-distribution-histogram.png) · [SVG](generated/salary-distribution-histogram.svg)

### Полная гистограмма в логарифмах

Включает весь хвост; интервалы равны в логарифмах.

![Полная гистограмма в логарифмах](generated/salary-distribution-loghist.png)

[PNG](generated/salary-distribution-loghist.png) · [SVG](generated/salary-distribution-loghist.svg)

### Накопленные распределения, ECDF

Отвечают на вопрос, какая доля вакансий ниже выбранного порога.

![Накопленные распределения, ECDF](generated/salary-distribution-ecdf.png)

[PNG](generated/salary-distribution-ecdf.png) · [SVG](generated/salary-distribution-ecdf.svg)

### Violin plot в логарифмах

Сравнивает сглаженную форму распределений по всем наблюдениям.

![Violin plot в логарифмах](generated/salary-distribution-violin.png)

[PNG](generated/salary-distribution-violin.png) · [SVG](generated/salary-distribution-violin.svg)

### Авторские профили плотности

Выносят каждую группу на отдельную полосу; высота нормирована внутри группы.

![Авторские профили плотности](generated/salary-distribution-ridgeline.png)

[PNG](generated/salary-distribution-ridgeline.png) · [SVG](generated/salary-distribution-ridgeline.svg)

## Полнота данных

Доля вакансий без зарплаты увеличивается от 5,2% в группе без опыта до 54,8% в группе более 6 лет. Сравниваемые зарплаты относятся только к записям, где зарплата указана. Это ограничение я учитываю при выводах. Данные: [data-quality.csv](data-quality.csv).

### Полнота данных

Основной вариант.

![Полнота данных](generated/salary-quality-missing.png)

[PNG](generated/salary-quality-missing.png) · [SVG](generated/salary-quality-missing.svg)

### Точки: доля пропусков

Выделяют только отсутствующие зарплаты на общей шкале 0–100%.

![Точки: доля пропусков](generated/salary-quality-dots.png)

[PNG](generated/salary-quality-dots.png) · [SVG](generated/salary-quality-dots.svg)

### Авторские карточки полноты

Соединяют процент пропусков, их число и объём доступных данных.

![Авторские карточки полноты](generated/salary-quality-cards.png)

[PNG](generated/salary-quality-cards.png) · [SVG](generated/salary-quality-cards.svg)


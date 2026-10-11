"""Короткий пример расчётов по сводной таблице; полный анализ — salary_analysis.py."""
import csv
from pathlib import Path
rows = list(csv.DictReader((Path(__file__).parent / 'salary-summary.csv').open(encoding='utf-8')))
assert sum(int(row['count']) for row in rows) == 74410
for row in rows:
    median = float(row['median_rub'])
    iqr = float(row['q75_rub']) - float(row['q25_rub'])
    print(f"{row['experience']}: IQR={iqr:.0f} RUB; IQR/median={100*iqr/median:.2f}%; mean/median={float(row['mean_rub'])/median:.3f}")

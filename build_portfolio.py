"""Пересобрать галерею и проверить её, сохраняя прежние файлы проекта."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import matplotlib
import numpy
import pandas as pd
import scipy

ROOT = Path(__file__).resolve().parent
CHARTS = [
    "salary-means-bars", "salary-means-dumbbell", "salary-means-cards",
    "salary-quartiles-interval", "salary-quartiles-boxplot", "salary-quartiles-normalized",
    "salary-cities-bars", "salary-cities-lollipop", "salary-cities-matrix",
    "salary-distribution-histogram", "salary-distribution-loghist",
    "salary-distribution-ecdf", "salary-distribution-violin", "salary-distribution-ridgeline",
    "salary-quality-missing", "salary-quality-dots", "salary-quality-cards",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, nargs="?", default=ROOT / "vacancies.csv.gz")
    parser.add_argument("--output", type=Path, default=ROOT / "generated")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(ROOT / "salary_analysis.py"), str(args.csv),
                    "--output", str(args.output)], check=True)
    checks = json.loads((args.output / "analysis-checks.json").read_text())
    summary = pd.read_csv(args.output / "salary-summary.csv")
    quality = pd.read_csv(args.output / "data-quality.csv")
    if checks["salary_rows"] + checks["missing_salary_rows"] != checks["rows"]:
        raise AssertionError("Не сходятся численности исходной выборки")
    if int(summary["count"].sum()) != checks["salary_rows"]:
        raise AssertionError("Не сходятся численности групп")
    if int(quality["size"].sum()) != checks["rows"]:
        raise AssertionError("Не сходится таблица качества")
    if not ((summary.q25_rub <= summary.median_rub) &
            (summary.median_rub <= summary.q75_rub)).all():
        raise AssertionError("Нарушен порядок квартилей")
    for name in CHARTS:
        for extension in ("png", "svg"):
            path = args.output / f"{name}.{extension}"
            if not path.is_file() or path.stat().st_size < 1000:
                raise AssertionError(f"Не создан график: {path.name}")

    report = "# Последняя сборка анализа зарплат\n\n"
    report += "Эта страница и 17 графиков пересчитываются из CSV. Числа ниже относятся к текущему файлу данных.\n\n"
    report += f"Строк: **{checks['rows']:,}**; с зарплатой: **{checks['salary_rows']:,}**; без зарплаты: **{checks['missing_salary_rows']:,}**.\n\n".replace(",", " ")
    report += f"Обратных вилок: **{checks['inverted_ranges']}**. SHA-256 распакованного CSV: `{checks['sha256']}`.\n\n"
    report += "| Опыт | Вакансий | Среднее, ₽ | Медиана, ₽ | Q1–Q3, ₽ |\n|---|---:|---:|---:|---:|\n"
    for row in summary.itertuples():
        report += f"| {row.experience} | {row.count} | {row.mean_rub:,.0f} | {row.median_rub:,.0f} | {row.q25_rub:,.0f}–{row.q75_rub:,.0f} |\n".replace(",", " ")
    report += "\n[Разбор проекта](../README.md) · [Галерея всех вариантов](../CHARTS.md) · [Сводная таблица](salary-summary.csv)\n\n"
    report += "Границы выводов: происхождение, период и валюта выгрузки не подтверждены; это учебная выборка. Пропуски и обратные вилки учитываются явно.\n"
    (args.output / "REPORT.md").write_text(report, encoding="utf-8")
    names = [f"{name}.{extension}" for name in CHARTS for extension in ("png", "svg")]
    names += ["salary-summary.csv", "sensitivity-summary.csv", "city-medians.csv",
              "city-counts.csv", "data-quality.csv", "analysis-checks.json", "REPORT.md"]
    manifest = {
        "source_csv_sha256": checks["sha256"], "chart_count": len(CHARTS),
        "checks": "passed", "versions": {"numpy": numpy.__version__, "pandas": pd.__version__,
        "scipy": scipy.__version__, "matplotlib": matplotlib.__version__},
        "code_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                        for name in ("salary_analysis.py", "build_portfolio.py", "requirements-rebuild.txt")},
        "files": {name: hashlib.sha256((args.output / name).read_bytes()).hexdigest() for name in names},
    }
    (args.output / "build-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Проверено: {len(CHARTS)} графиков в PNG/SVG, 5 сводных CSV; прежние материалы сохранены.")


if __name__ == "__main__":
    main()

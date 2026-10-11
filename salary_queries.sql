-- Учебные примеры для SQLite. Перед запуском импортируйте CSV в таблицу vacancies.
-- salary_from и salary_to должны быть числовыми; отсутствующие значения — NULL.
-- Две границы дают середину вилки, одна граница — указанное значение.

WITH prepared AS (
  SELECT *, CASE
    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL
      THEN (salary_from + salary_to) / 2.0
    ELSE COALESCE(salary_from, salary_to)
  END AS salary
  FROM vacancies
)
SELECT experience, COUNT(salary) AS salary_count,
       ROUND(AVG(salary), 2) AS mean_salary_rub,
       ROUND(100.0 * SUM(salary IS NULL) / COUNT(*), 2) AS missing_salary_percent
FROM prepared
GROUP BY experience;

-- Сравнение городов внутри одной категории опыта. Медианы — в Python-скрипте.
WITH prepared AS (
  SELECT *, CASE
    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL
      THEN (salary_from + salary_to) / 2.0
    ELSE COALESCE(salary_from, salary_to)
  END AS salary
  FROM vacancies
)
SELECT city, COUNT(salary) AS salary_count, ROUND(AVG(salary), 2) AS mean_salary_rub
FROM prepared
WHERE experience = 'От 1 года до 3 лет' AND salary IS NOT NULL
GROUP BY city
ORDER BY mean_salary_rub DESC;

-- Диагностика качества. Обратная вилка — повод проверить строку.
SELECT COUNT(*) AS total_rows,
       SUM(salary_from IS NULL AND salary_to IS NULL) AS missing_salary_rows,
       SUM(salary_from IS NOT NULL AND salary_to IS NOT NULL
           AND salary_from > salary_to) AS inverted_ranges,
       COUNT(*) - COUNT(DISTINCT vacancy_id) AS duplicate_ids
FROM vacancies;

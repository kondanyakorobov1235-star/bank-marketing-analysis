-- Общая доля положительных ответов.
SELECT COUNT(*) AS contacts, SUM(subscribed) AS subscriptions,
       ROUND(100.0 * AVG(subscribed), 2) AS conversion_pct FROM bank;
-- Конверсия по виду занятости: размер группы обязателен для интерпретации.
SELECT job, COUNT(*) AS contacts, SUM(subscribed) AS subscriptions,
       ROUND(100.0 * AVG(subscribed), 2) AS conversion_pct
FROM bank GROUP BY job ORDER BY contacts DESC;
-- Результат предыдущей кампании, включая неизвестные значения.
SELECT poutcome, COUNT(*) AS contacts, SUM(subscribed) AS subscriptions,
       ROUND(100.0 * AVG(subscribed), 2) AS conversion_pct
FROM bank GROUP BY poutcome ORDER BY contacts DESC;

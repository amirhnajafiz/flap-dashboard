--- Count the number of times a file was accesses (just read/write)
SELECT COUNT(*) AS fcount, fname, event_name, SUM(ret) AS fbytes, SUM(ex_timestamp - en_timestamp) AS fdur
FROM io_logs
WHERE fname is NOT NULL AND fname <> ''
GROUP BY fname, event_name
HAVING event_name LIKE '%read%' OR event_name LIKE '%write%'
ORDER BY fcount;

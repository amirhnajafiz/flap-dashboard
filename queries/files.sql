--- Count the number of times a file was accesses (just read/write)
SELECT COUNT(*) AS fcount, fname, event_name, SUM(ret) AS fbytes, SUM(ex_timestamp - en_timestamp) AS fdur
FROM io_logs
WHERE fname is NOT NULL AND fname <> ''
GROUP BY fname, event_name
HAVING event_name LIKE '%read%' OR event_name LIKE '%write%'
ORDER BY fcount;

--- Find the percentage of unknown operations
SELECT 
    (100.0 * 
        SUM(CASE WHEN fname IS NULL OR fname = '' OR fname = 'unknown' THEN 1 ELSE 0 END)
    ) / NULLIF(COUNT(*), 0) 
AS percent_unknown
FROM io_logs;

--- Find the percentage of read operations
SELECT 
    (100.0 * 
        SUM(CASE WHEN event_name LIKE '%read%' THEN 1 ELSE 0 END)
    ) / NULLIF(COUNT(*), 0) 
AS percent_read
FROM io_logs;

--- Find the percentage of write operations
SELECT 
    (100.0 * 
        SUM(CASE WHEN event_name LIKE '%write%' THEN 1 ELSE 0 END)
    ) / NULLIF(COUNT(*), 0) 
AS percent_write
FROM io_logs;

--- Find the percentage of mmap operations
SELECT 
    (100.0 * 
        SUM(CASE WHEN event_name LIKE '%mmap%' THEN 1 ELSE 0 END)
    ) / NULLIF(COUNT(*), 0) 
AS percent_mmap
FROM io_logs;

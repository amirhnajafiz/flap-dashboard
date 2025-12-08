UPDATE io_logs
SET fname = COALESCE(
    (
        SELECT m2.fname
        FROM (
            SELECT MAX(m1.en_timestamp) AS ts
            FROM meta_logs m1
            WHERE m1.proc = io_logs.proc
              AND m1.ret = io_logs.fd
              AND m1.en_timestamp <= io_logs.en_timestamp
        ) AS best
        JOIN meta_logs m2
            ON m2.proc = io_logs.proc
           AND m2.ret = io_logs.fd
           AND m2.en_timestamp = best.ts
        LIMIT 1
    ),
    'unknown'
)
WHERE fname IS NULL OR fname = '';

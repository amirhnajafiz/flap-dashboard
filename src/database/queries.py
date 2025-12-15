UPDATE_FD_FNAME_VALUES = """
UPDATE io_logs
SET fname = CASE
    WHEN fd = 0 THEN 'stdin'
    WHEN fd = 1 THEN 'stdout'
    WHEN fd = 2 THEN 'stderr'
END
WHERE fd IN (0, 1, 2);
"""

UPDATE_IO_FNAME_VALUES = """
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

    CASE io_logs.fd
        WHEN 0 THEN 'stdin'
        WHEN 1 THEN 'stdout'
        WHEN 2 THEN 'stderr'
        ELSE NULL
    END,

    'unknown'
)
WHERE fname IS NULL OR fname = '';
"""

UPDATE_MEMORY_FNAME_VALUES = """
UPDATE memory_logs
SET fname = COALESCE(
    (
        SELECT m2.fname
        FROM (
            SELECT MAX(m1.en_timestamp) AS ts
            FROM meta_logs m1
            WHERE m1.proc = memory_logs.proc
              AND m1.ret = memory_logs.fd
              AND m1.en_timestamp <= memory_logs.en_timestamp
        ) AS best
        JOIN meta_logs m2
            ON m2.proc = memory_logs.proc
           AND m2.ret = memory_logs.fd
           AND m2.en_timestamp = best.ts
        LIMIT 1
    ),

    CASE memory_logs.fd
        WHEN 0 THEN 'stdin'
        WHEN 1 THEN 'stdout'
        WHEN 2 THEN 'stderr'
        ELSE NULL
    END,

    'unknown'
)
WHERE fname IS NULL OR fname = '';
"""

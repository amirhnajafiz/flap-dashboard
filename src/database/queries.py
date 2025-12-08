CREATE_META_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS meta_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    en_timestamp BIGINT,
    en_datetime TEXT,
    ex_timestamp BIGINT,
    ex_datetime TEXT,
    pid INT,
    tid INT,
    proc TEXT,
    event_name TEXT,
    fname TEXT,
    ret INT
);
"""

CREATE_IO_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS io_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    en_timestamp BIGINT,
    en_datetime TEXT,
    ex_timestamp BIGINT,
    ex_datetime TEXT,
    pid INT,
    tid INT,
    proc TEXT,
    event_name TEXT,
    fd INT,
    ret INT,
    countbytes INT,
    fname TEXT
);
"""

CREATE_META_LOGS_INDEX = """
CREATE INDEX IF NOT EXISTS idx_meta_proc_ret_ts
ON meta_logs (proc, ret, en_timestamp);
"""

CREATE_IO_LOGS_INDEX = """
CREATE INDEX IF NOT EXISTS idx_io_proc_fd_ts
ON io_logs (proc, fd, en_timestamp);
"""

UPDATE_FNAME_VALUES = """
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
"""

INSERT_META_LOG_RECORD = """
INSERT INTO meta_logs (
    en_timestamp, en_datetime, ex_timestamp, ex_datetime, pid, tid, proc, event_name, fname, ret
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

INSERT_IO_LOG_RECORD = """
INSERT INTO io_logs (
    en_timestamp, en_datetime, ex_timestamp, ex_datetime, pid, tid, proc, event_name, fd, ret, countbytes
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

GET_IO_LOGS = """
SELECT * FROM io_logs;
"""

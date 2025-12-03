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
    ret INT
);
"""

INSERT_META_LOG_RECORD = """
INSERT INTO meta_logs (
    en_timestamp, en_datetime, ex_timestamp, ex_datetime, pid, tid, proc, event_name, fname, ret
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

INSERT_IO_LOG_RECORD = """
INSERT INTO io_logs (
    en_timestamp, en_datetime, ex_timestamp, ex_datetime, pid, tid, proc, event_name, fd, ret
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

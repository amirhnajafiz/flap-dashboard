CREATE_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    en_timestamp BIGINT,
    en_datetime TEXT,
    ex_timestamp BIGINT,
    ex_datetime TEXT,
    pid INT,
    tid INT,
    proc TEXT,
    event_name TEXT,
    event_type TEXT,
    parameters TEXT
);
"""

INSERT_LOG_RECORD = """
INSERT INTO logs (
    en_timestamp, en_datetime, ex_timestamp, ex_datetime, pid, tid, proc, event_name, event_type, parameters
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

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

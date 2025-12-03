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

CREATE_IO_VIEW = """
CREATE VIEW IF NOT EXISTS io_v AS
SELECT
    id,
    pid,
    tid,
    proc,
    event_name,
    fd,
    en_timestamp,
    ex_timestamp,
    en_datetime,
    ex_datetime
FROM io_logs;
"""

CREATE_IO_CAND_VIEW = """
CREATE VIEW IF NOT EXISTS io_cand_v AS
SELECT
    io.id   AS io_id,
    m.fname AS fname,
    ABS(io.en_timestamp - m.en_timestamp) AS dt
FROM io_v AS io
JOIN meta_logs AS m
  ON  m.pid = io.pid
  AND m.ret = io.fd
  AND m.ret >= 0
  AND io.en_timestamp >= m.en_timestamp;
"""

CREATE_IO_BEST_VIEW = """
CREATE VIEW IF NOT EXISTS io_best_v AS
SELECT io_id, fname
FROM (
    SELECT
        io_id,
        fname,
        ROW_NUMBER() OVER (PARTITION BY io_id ORDER BY dt) AS rn
    FROM io_cand_v
) AS ranked
WHERE rn = 1;
"""

CREATE_IO_FNAME_VIEW = """
CREATE VIEW IF NOT EXISTS io_with_fname_v AS
SELECT
    io.id,
    io.pid,
    io.tid,
    io.proc,
    io.event_name,
    io.fd,
    io.en_timestamp,
    io.ex_timestamp,
    io.en_datetime,
    io.ex_datetime,
    COALESCE(best.fname, 'unknown') AS fname
FROM io_v AS io
LEFT JOIN io_best_v AS best
  ON best.io_id = io.id;
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

GET_IO_EVENTS = """
SELECT * FROM io_with_fname_v ORDER BY id ASC;
"""

WITH 
    fdpid AS (
        SELECT DISTINCT fd, pid, event_name, en_timestamp, ex_timestamp, ret
        FROM io_logs 
        WHERE event_name = "mmap" AND fd <> -1
    ),
    result AS (
        SELECT
            fdpid.*,
            (
                SELECT fname
                FROM meta_logs AS m
                WHERE m.pid = fdpid.pid
                AND m.ret = fdpid.fd
                AND m.en_timestamp <= fdpid.en_timestamp
                ORDER BY m.en_timestamp DESC
                LIMIT 1
            ) AS fname
        FROM fdpid
    )
SELECT result.ret, result.fname, COUNT(*) as fcount
FROM result
GROUP BY result.fname;

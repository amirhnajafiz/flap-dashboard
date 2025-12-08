CREATE INDEX IF NOT EXISTS idx_meta_proc_ret_ts
ON meta_logs (proc, ret, en_timestamp);

CREATE INDEX IF NOT EXISTS idx_io_proc_fd_ts
ON io_logs (proc, fd, en_timestamp);

# FLAP Dashboard

Challenges:

- Large volume of logs
- Queries take too long

Solutions:

- Separate PID,TID tracing process.
    - For each PID (or procname)
        - For each TID
- Separate DUP syscalls.
- Use predefined queries to prepare your data once.
- Drop unused tables.
- Don't use views.
- Tune the database for faster throughput.

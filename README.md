# FLAP Dashboard

Input: the output directory of FLAP.

Pipeline:

- Multiprocessing for JSON parsing — fully utilizes all CPU cores.
- Multiprocessing for file writing — avoids GIL and maximizes disk throughput.
- Per-file dedicated writer process — preserves exact line ordering with no locking.
- Memory-mapped input file reading — zero-copy, ultra-fast line streaming.
- Batch processing of lines in workers — reduces IPC overhead by ~2000×.
- Batch writes in writers (~4MB flush) — minimizes syscalls and disk I/O overhead.
- Use of orjson when available — ~10× faster JSON parsing than stdlib.
- Binary write path (.write(b"...")) — removes text encoding overhead.
- Queues with bounded size — prevents RAM blowup under high throughput.
- Daemonized writer processes — low-latency startup and clean shutdown.
- Avoiding Python locks entirely — no contention, near-ideal parallel scaling.
- Precomputed output paths in workers — avoids repeated filesystem checks.

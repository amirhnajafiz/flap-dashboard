# file: pipeline

import sys
import os
import mmap
import multiprocessing as mp
from multiprocessing import Process, Queue
import time

try:
    import orjson as json  # ultra-fast JSON parser (10x faster than json)
except ImportError:
    import json # relatively slow



# Configurations
BATCH_LINES = 2000               # worker batch size (batch writes per file writer)
WRITE_BATCH_BYTES = 4*1024*1024  # writer flush threshold, writer processes flush instead of per-line (default 4MB)


# -------------------------------
# Writer Process
# -------------------------------
def writer_process_func(path: str, q: Queue):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    buf = []
    total_bytes = 0

    with open(path, "ab", buffering=0) as f:
        while True:
            item = q.get()
            if item is None:  # shutdown
                break

            buf.append(item)
            total_bytes += len(item)

            if total_bytes >= WRITE_BATCH_BYTES:
                f.write(b"".join(buf))
                buf.clear()
                total_bytes = 0

        # final flush
        if buf:
            f.write(b"".join(buf))


# -------------------------------
# Create / lookup writer queue
# -------------------------------
writer_queues = {}
writer_processes = {}

def get_writer_queue(path: str):
    if path not in writer_queues:
        q = mp.Queue(maxsize=8000)
        writer_queues[path] = q

        p = Process(target=writer_process_func, args=(path, q), daemon=True)
        writer_processes[path] = p
        p.start()

    return writer_queues[path]


# -------------------------------
# Worker: parse batch of JSON lines
# -------------------------------
def process_batch(args):
    base_dir, lines = args
    out = []

    for line in lines:
        try:
            log = json.loads(line)
        except:
            continue

        proc = log.get("proc")
        if not proc:
            continue

        operand = log["operand"]
        out_dir = os.path.join(base_dir, "procs", proc)
        out_path = os.path.join(out_dir, f"{operand}.jsonl")

        out.append((out_path, (line + "\n").encode("utf-8")))

    return out


# -------------------------------
# Memory-Mapped Reader
# -------------------------------
def read_lines_mmap(path):
    """Stream lines extremely fast using mmap (zero copy)."""
    with open(path, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        line = mm.readline()
        while line:
            yield line.rstrip(b"\n").decode("utf-8")
            line = mm.readline()
        mm.close()


# -------------------------------
# Main indexer
# -------------------------------
def index_logs(base_dir: str, workers=mp.cpu_count()):
    log_path = os.path.join(base_dir, "logs.jsonl")

    pool = mp.Pool(workers)
    count = 0
    batch = []

    for line in read_lines_mmap(log_path):
        batch.append(line)

        if len(batch) >= BATCH_LINES:
            for out_path, raw in pool.apply_async(process_batch, ((base_dir, batch),)).get():
                q = get_writer_queue(out_path)
                q.put(raw)
            count += len(batch)
            batch.clear()

            if count % BATCH_LINES == 0:
                print(f"indexing at {count} ...")

    # last partial batch
    if batch:
        for out_path, raw in pool.apply_async(process_batch, ((base_dir, batch),)).get():
            q = get_writer_queue(out_path)
            q.put(raw)
        count += len(batch)

    pool.close()
    pool.join()

    return count, log_path


# -------------------------------
# Shutdown writers
# -------------------------------
def shutdown_writers():
    for q in writer_queues.values():
        q.put(None)
    for p in writer_processes.values():
        p.join()


# -------------------------------
# Entrypoint
# -------------------------------
def main(dir: str):
    start_time = time.perf_counter() 

    base = dir
    print(f"loading {base} ...")

    total, path = index_logs(base)
    shutdown_writers()

    end_time = time.perf_counter()

    execution_time = end_time - start_time
    print(f"\nexecuted in: {execution_time:.4f} seconds")
    print(f"Done: indexed {total} entries from {path}")
    print("And that's The Fate of Ophelia!")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("must provide logs directory.")
        sys.exit(1)

    main(sys.argv[1])

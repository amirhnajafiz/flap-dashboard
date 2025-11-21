import json
import pandas as pd
import numpy as np
import plotly.express as px
from astropy.stats import bayesian_blocks



LOGS = "logs/procs"
PROC = "vllm"
OPRD = ["mmap", "read", "write"]

def load_logs(path):
    for line in open(path):
        yield json.loads(line)

def pair_events(path, operand):
    pending = {}
    rows = []

    for ev in load_logs(path):
        key = (ev["tid"], ev["operand"], ev["details"]["fd"])

        if ev["event_type"] == "ENTER":
            pending[key] = ev
            continue

        if ev["event_type"] == "EXIT" and key in pending:
            _ = pending.pop(key)
            rows.append({
                "latency_ms": int(ev["details"]["latency"]) / 1_000_000,
                "operand": operand
            })

    return pd.DataFrame(rows)

def main():
    dfs = []

    for op in OPRD:
        df = pair_events(f"{LOGS}/{PROC}/{op}.jsonl", op)
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)

    # =======================================
    # Compute entropy-optimal bin edges
    # =======================================
    bbins = bayesian_blocks(df["latency_ms"].values)  # <-- MAGIC
    # Plotly expects uniform bins, so we manually pass edges
    xbins = dict(
        start=float(bbins[0]),
        end=float(bbins[-1]),
        size=None  # size ignored when we pass edges
    )

    fig = px.histogram(
        df,
        x="latency_ms",
        color="operand",
        title=f"Latency Distribution for {PROC} : {', '.join(OPRD)}",
        labels={"latency_ms": "Latency (ms)", "operand": "Operand"},
        opacity=0.6
    )

    # Override bin edges to Bayesian Blocks
    fig.update_traces(xbins=xbins, autobinx=False)
    fig.update_yaxes(type="log")

    fig.update_layout(
        bargap=0.05,
        height=1000
    )

    fig.show()

if __name__ == "__main__":
    main()

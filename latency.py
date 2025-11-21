import json
import pandas as pd
import plotly.express as px



LOGS = "logs/procs"
PROC = "vllm"
OPRD = "mmap"

def load_logs(path):
    for line in open(path):
        yield json.loads(line)

def pair_events(path):
    pending = {}
    rows = []

    for ev in load_logs(path):
        key = (ev["tid"], ev["operand"], ev["details"]["fd"])

        if ev["event_type"] == "ENTER":
            pending[key] = ev
            continue

        if ev["event_type"] == "EXIT" and key in pending:
            _ = pending.pop(key)
            rows.append(int(ev["details"]["latency"]) / 1000000)

    return pd.DataFrame({"latency_us": rows})

def main():
    df = pair_events(f'{LOGS}/{PROC}/{OPRD}.jsonl')

    fig = px.histogram(
        df,
        x="latency_us",
        nbins=200,
        title=f"Latency Distribution {PROC} : {OPRD}",
        labels={"latency_us": "Latency (ms)"},
    )

    fig.update_layout(
        bargap=0.05,
        height=1000
    )

    fig.show()

if __name__ == "__main__":
    main()

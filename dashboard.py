import json
import os
from datetime import datetime
import plotly.express as px
import pandas as pd



def parse_timestamp(ts):
    """Support timestamps with or without microseconds."""
    try:
        return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")

def choose(options, title):
    print(f"\n=== {title} ===")
    for i, op in enumerate(options):
        print(f"{i}: {op}")
    idx = int(input("Choose index: "))
    return options[idx]


def load_events(jsonl_path):
    events = []
    with open(jsonl_path, "r") as f:
        for line in f:
            obj = json.loads(line)
            obj["ts"] = parse_timestamp(obj["timestamp"])
            events.append(obj)
    return events


def build_pairs(events):
    """
    Convert ENTER/EXIT events into intervals.
      ENTER → start_ts
      EXIT  → end_ts
    Returns list of dicts:
    {start, end, fname}
    """
    stack = {}  # key: (tid, fd, fname)
    intervals = []

    for ev in events:
        fname = ev["details"].get("fname", "unknown")
        fd = ev["details"].get("fd")
        key = (ev["tid"], fd, fname)

        if ev["event_type"] == "ENTER":
            stack[key] = ev["ts"]
        elif ev["event_type"] == "EXIT":
            start = stack.pop(key, None)
            if start:
                end = ev["ts"]
                mid = start + (end - start) / 2
                intervals.append({
                    "start": start,
                    "end": end,
                    "midpoint": mid,
                    "fname": fname
                })

    return intervals


def main():
    root = input("Logs directory path: ").strip()
    procs_dir = os.path.join(root, "procs")

    # List processes
    procs = sorted(os.listdir(procs_dir))
    proc = choose(procs, "Available Processes")

    proc_path = os.path.join(procs_dir, proc)

    # List operand JSONL files
    json_files = [f for f in os.listdir(proc_path) if f.endswith(".jsonl")]
    operands = [f.replace(".jsonl", "") for f in json_files]

    operand = choose(operands, "Available Operands")

    jsonl_path = os.path.join(proc_path, f"{operand}.jsonl")

    # Load events
    events = load_events(jsonl_path)

    # Build ENTER–EXIT pairs
    intervals = build_pairs(events)

    if not intervals:
        print("No intervals found.")
        return

    # Create DataFrame for Plotly
    df = pd.DataFrame(intervals)

    # Main timeline
    fig = px.timeline(
        df, 
        x_start="start",
        x_end="end",
        y="fname",
        title=f"Timeline for {proc} / {operand}"
    )

    # Flip y-axis
    fig.update_yaxes(tickformat=".9f")

    # Add marker points for midpoints (to know where to zoom)
    fig.add_scatter(
        x=df["midpoint"],
        y=df["fname"],
        mode="markers",
        marker=dict(size=6, opacity=0.4),
        name="activity"
    )

    # Sliding time window
    fig.update_xaxes(rangeslider_visible=True)

    fig.show()


if __name__ == "__main__":
    main()

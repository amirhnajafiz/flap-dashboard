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


def build_pairs(events, merge_threshold_s=1.0):
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
                intervals.append({
                    "start": start,
                    "end": end,
                    "fname": fname,
                    "tid": ev["tid"],
                    "fd": fd
                })

    # Sort intervals by key and start time
    intervals.sort(key=lambda x: (x["tid"], x["fd"], x["fname"], x["start"]))

    # Merge close intervals
    merged = []
    for interval in intervals:
        if merged:
            last = merged[-1]
            same_key = (last["tid"], last["fd"], last["fname"]) == (interval["tid"], interval["fd"], interval["fname"])
            close = (interval["start"] - last["end"]).total_seconds() < merge_threshold_s
            if same_key and close:
                # extend the previous interval
                last["end"] = max(last["end"], interval["end"])
                last["midpoint"] = last["start"] + (last["end"] - last["start"]) / 2
                continue
        interval["midpoint"] = interval["start"] + (interval["end"] - interval["start"]) / 2
        merged.append(interval)

    return merged


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

    # -------------------------
    #  BEAUTIFY TIMELINE LINES
    # -------------------------

    # Make lines thick & bright
    fig.update_traces(
        marker=dict(color="rgba(0,0,0,1)"),  # dark solid line
        base=dict(width=8)                   # thicker
    )

    # -------------------------
    #  MIDPOINT MARKERS (RED)
    # -------------------------

    fig.add_scatter(
        x=df["midpoint"],
        y=df["fname"],
        mode="markers",
        marker=dict(
            size=10,
            opacity=0.25,
            color="red"
        ),
        name="midpoint"
    )

    # -------------------------
    #  START + END MARKERS (GREEN)
    # -------------------------

    fig.add_scatter(
        x=df["start"],
        y=df["fname"],
        mode="markers",
        marker=dict(
            size=12,
            opacity=0.4,
            color="green"
        ),
        name="start"
    )

    fig.add_scatter(
        x=df["end"],
        y=df["fname"],
        mode="markers",
        marker=dict(
            size=12,
            opacity=0.4,
            color="green"
        ),
        name="end"
    )

    # Flip y-axis
    fig.update_yaxes(tickformat=".9f")

    # Sliding window
    fig.update_xaxes(rangeslider_visible=True)

    fig.show()


if __name__ == "__main__":
    main()

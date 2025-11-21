import json
import pandas as pd
import plotly.express as px



LOGS = "logs/procs"
PROC = "vllm"
OPRD = ["mmap", "read", "write"]
KEYWORD = "/root"

MIN_VISIBLE_US = 1000000     # minimum visual width (adjust as needed)

def load_events(path):
    events = []
    with open(path) as f:
        for line in f:
            ts, name = line.strip().split(" ", 1)
            # Combine the date+time part (2 tokens)
            # Example line: "2025-11-19 09:05:32 init"
            date, time, label = line.strip().split(" ", 2)
            ts = pd.to_datetime(date + " " + time)
            events.append({"timestamp": ts, "event": label})
    return pd.DataFrame(events)

def load_logs(path):
    for line in open(path):
        yield json.loads(line)

def pair_events(path):
    pending = {}
    rows = []

    for ev in load_logs(path):
        tid = ev["tid"]
        op = ev["operand"]
        fd = ev["details"]["fd"]

        key = (tid, op, fd)

        if ev["event_type"] == "ENTER":
            pending[key] = ev
            continue

        if ev["event_type"] == "EXIT" and key in pending:
            en = pending.pop(key)
            if KEYWORD in ev["details"]["fname"]:
                rows.append({
                    "operand": op,
                    "fname": ev["details"]["fname"],
                    "start": en["timestamp"],
                    "end": ev["timestamp"],
                    "latency_us": int(ev["details"]["latency"]),
                })

    return pd.DataFrame(rows)


def plot_timeline(df, events_df):
    df["start"] = pd.to_datetime(df["start"])
    df["end"] = pd.to_datetime(df["end"])

    # Compute real latency
    df["latency_us"] = df["latency_us"].astype(int)

    # Create visual end time that’s always visible
    df["duration_us"] = df["latency_us"]
    df["end_visual"] = df["end"]

    # Fix tiny durations
    mask = df["duration_us"] < MIN_VISIBLE_US
    df.loc[mask, "end_visual"] = df.loc[mask, "start"] + pd.to_timedelta(MIN_VISIBLE_US, unit="us")

    # Hover info
    df["hover"] = (
        "File: " + df["fname"] +
        "<br>Latency: " + df["latency_us"].astype(str) + " µs" +
        "<br>Start: " + df["start"].astype(str) +
        "<br>End: " + df["end"].astype(str) +
        "<br>Visual duration: " + df["duration_us"].astype(str) + " → forced min"
    )

    # Build timeline
    fig = px.timeline(
        df,
        x_start="start",
        x_end="end_visual",   # <-- shown visually
        y="operand",
        color="operand",
        hover_data={"hover": True},
        title=f"Timeline of File Operations {PROC} : {', '.join(OPRD)}",
    )

    fig.update_yaxes(title="Operand")
    fig.update_xaxes(title="Time")

    for index, row in events_df.iterrows():
        ts = row["timestamp"]
        label = row["event"]

        fig.add_vline(
            x=ts,
            line_width=1,
            line_dash="dash",
            line_color="red",
        )

        fig.add_annotation(
            x=ts,
            y=1.02 if index % 2 == 0 else 1.03,
            xref="x",
            yref="paper",
            showarrow=False,
            text=label,
            font=dict(size=10)
        )
    
    fig.show()


def main():
    all_data = []
    for op in OPRD:
        data = pair_events(f"{LOGS}/{PROC}/{op}.jsonl")
        all_data.append(data)
    
    df = pd.concat(all_data, ignore_index=True)

    events_df = load_events("events.logs")
    plot_timeline(df, events_df)


if __name__ == "__main__":
    main()

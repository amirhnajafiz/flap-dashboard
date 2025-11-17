#!/usr/bin/env python3
import sys
import json
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go

# Usage:
#   ./plot_traces.py <logfile>

if len(sys.argv) < 2:
    print("Usage: ./plot_traces.py <logfile>")
    sys.exit(1)

log_file = Path(sys.argv[1])

# read the json logs
with open(f"{log_file}.json", 'r') as file:
    prefix_times = json.load(file)

# Flatten data and collect all counts
all_counts = []
for prefix, time_counts in prefix_times.items():
    all_counts.extend(time_counts.values())

min_count = min(all_counts)
max_count = max(all_counts)

def scale_size(count, min_size=6, max_size=30):
    if max_count == min_count:
        return (min_size + max_size) / 2
    return min_size + (count - min_count) / (max_count - min_count) * (max_size - min_size)

# Build interactive scatter plot
fig = go.Figure()

# Add one scatter per prefix
for prefix, time_counts in sorted(prefix_times.items()):
    times = [datetime.strptime(t, "%Y-%m-%d %H:%M:%S") for t in time_counts.keys()]
    counts = list(time_counts.values())
    sizes = [scale_size(c) for c in counts]

    fig.add_trace(
        go.Scattergl(
            x=times,
            y=[prefix] * len(times),
            mode="markers",
            marker=dict(size=sizes, opacity=0.7),
            name=f"{prefix} ({sum(counts)})",
            hovertemplate="<b>%{y}</b><br>Time: %{x|%H:%M:%S}<br>Count: %{customdata}<extra></extra>",
            customdata=counts
        )
    )

# define event times
DATE = "2025-11-10"

def to_dt(t):
    return datetime.strptime(f"{DATE} {t}", "%Y-%m-%d %H:%M:%S")

events = {
    "tracing start": to_dt("09:39:16"),
    "container start": to_dt("09:39:22"),
    "config phase start": to_dt("09:39:22"),
    "config phase end": to_dt("09:39:55"),
    "loading phase start": to_dt("09:39:55"),
    "loading phase end": to_dt("09:42:13"),
    "compile phase start": to_dt("09:42:19"),
    "compile phase end": to_dt("09:43:04"),
    "memory profiling start": to_dt("09:43:05"),
    "memory profiling end": to_dt("09:43:06"),
    "graph capture start": to_dt("09:43:06"),
    "graph capture end": to_dt("09:43:17"),
    "vLLM ready": to_dt("09:43:19"),
    "tracing stopped": to_dt("09:46:40"),
}

# add shaded phases
fig.add_vrect(
    x0=events["config phase start"], x1=events["config phase end"],
    fillcolor="LightSalmon", opacity=0.3, layer="below", line_width=0,
    annotation_text="Config Phase", annotation_position="top left"
)
fig.add_vrect(
    x0=events["loading phase start"], x1=events["loading phase end"],
    fillcolor="LightSkyBlue", opacity=0.3, layer="below", line_width=0,
    annotation_text="Loading Phase", annotation_position="top left"
)
fig.add_vrect(
    x0=events["compile phase start"], x1=events["compile phase end"],
    fillcolor="LightGreen", opacity=0.3, layer="below", line_width=0,
    annotation_text="Compile Phase", annotation_position="top left"
)
fig.add_vrect(
    x0=events["memory profiling start"], x1=events["memory profiling end"],
    fillcolor="Black", opacity=0.3, layer="below", line_width=0,
    annotation_text="Mem Prof", annotation_position="top left",
    annotation_y=1.02
)
fig.add_vrect(
    x0=events["graph capture start"], x1=events["graph capture end"],
    fillcolor="Khaki", opacity=0.3, layer="below", line_width=0,
    annotation_text="Graph Capture", annotation_position="top left",
)

# key event lines
for label in ["tracing start", "container start", "vLLM ready", "tracing stopped"]:
    t = events[label]
    fig.add_vline(x=t, line_dash="dot", line_color="black", opacity=0.8)
    fig.add_annotation(
        x=t,
        y=1.06,
        xref="x",
        yref="paper",
        text=label.replace("_", " ").title(),
        showarrow=False,
        font=dict(size=10, color="black"),
        align="center",
        textangle=-20 if label in ["tracing start", "container start"] else 0
    )

fig.update_layout(
    title="File Access Timeline by Prefix (per-second resolution)",
    xaxis_title="Time (seconds)",
    yaxis_title="Path Prefix (first N levels)",
    height=1000,
    template="plotly",
    legend=dict(
        title="Path Prefixes",
        orientation="v",
        yanchor="top",
        y=0.98,
        xanchor="left",
        x=1.02
    ),
    margin=dict(r=200)
)

fig.update_xaxes(
    tickformat="%H:%M:%S",
    rangeslider_visible=True,
    showgrid=True
)

fig.show()

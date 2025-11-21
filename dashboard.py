import os
import json
import pandas as pd
import numpy as np
import plotly.express as px
from astropy.stats import bayesian_blocks

from dash import Dash, dcc, html, Input, Output, State

# ==== Default app-wide settings (edit as preferred)
LOGS = "logs/procs"
DEFAULT_PROC = "vllm"
DEFAULT_OPRDS = ["mmap", "read", "write"]
DEFAULT_KEYWORD = "/root"
EVENTS_FILE = "events.logs"
MIN_VISIBLE_US = 1000000

# -------------------------
# Utility functions (from your scripts)
def load_logs(path):
    if not os.path.isfile(path): return
    with open(path) as f:
        for line in f:
            yield json.loads(line)

def load_events(path):
    events = []
    if not os.path.isfile(path): return pd.DataFrame()
    with open(path) as f:
        for line in f:
            date, time, label = line.strip().split(" ", 2)
            ts = pd.to_datetime(date + " " + time)
            events.append({"timestamp": ts, "event": label})
    return pd.DataFrame(events)

def pair_events_timeline(path, keyword):
    pending = {}
    rows = []
    for ev in load_logs(path) or []:
        tid = ev["tid"]
        op = ev["operand"]
        fd = ev["details"]["fd"]
        key = (tid, op, fd)
        if ev["event_type"] == "ENTER":
            pending[key] = ev
            continue
        if ev["event_type"] == "EXIT" and key in pending:
            en = pending.pop(key)
            if len(keyword) != 0 and keyword not in ev["details"]["fname"]:
                continue

            rows.append({
                "operand": op,
                "fname": ev["details"]["fname"],
                "start": en["timestamp"],
                "end": ev["timestamp"],
                "latency_us": int(ev["details"]["latency"]),
            })
    return pd.DataFrame(rows)

def pair_events_latency(path, keyword, operand):
    pending = {}
    rows = []
    for ev in load_logs(path) or []:
        key = (ev["tid"], ev["operand"], ev["details"]["fd"])
        if ev["event_type"] == "ENTER":
            pending[key] = ev
            continue
        if ev["event_type"] == "EXIT" and key in pending:
            _ = pending.pop(key)
            if keyword in ev["details"]["fname"]:
                rows.append({
                    "latency_ms": int(ev["details"]["latency"]) / 1_000_000,
                    "operand": operand
                })
    return pd.DataFrame(rows)

def pair_events_files(path, keyword):
    pending = {}
    rows = []
    for ev in load_logs(path) or []:
        key = (ev["tid"], ev["operand"], ev["details"]["fd"])
        if ev["event_type"] == "ENTER":
            pending[key] = ev
            continue
        if ev["event_type"] == "EXIT" and key in pending:
            _ = pending.pop(key)
            if keyword in ev["details"]["fname"]:
                rows.append({
                    "fname": ev["details"]["fname"],
                    "operand": ev["operand"],
                    "latency_us": int(ev["details"]["latency"]) / 1000.0,
                })
    return pd.DataFrame(rows)

# ----------------------
# Plotting functions (adapted for interactive use)
def timeline_plot(proc, keyword, oprds):
    all_data = []
    for op in oprds:
        path = f"{LOGS}/{proc}/{op}.jsonl"
        data = pair_events_timeline(path, keyword)
        if not data.empty: all_data.append(data)
    if not all_data:
        return px.scatter(title="No matching data!")
    df = pd.concat(all_data, ignore_index=True)
    events_df = load_events(EVENTS_FILE)
    if df.empty:
        return px.scatter(title="No matching data!")

    df["start"] = pd.to_datetime(df["start"])
    df["end"] = pd.to_datetime(df["end"])
    df["latency_us"] = df["latency_us"].astype(int)
    df["duration_us"] = df["latency_us"]
    df["end_visual"] = df["end"]
    mask = df["duration_us"] < MIN_VISIBLE_US
    df.loc[mask, "end_visual"] = df.loc[mask, "start"] + pd.to_timedelta(MIN_VISIBLE_US, unit="us")
    df["hover"] = (
        "File: " + df["fname"] +
        "<br>Latency: " + df["latency_us"].astype(str) + " µs" +
        "<br>Start: " + df["start"].astype(str) +
        "<br>End: " + df["end"].astype(str) +
        "<br>Visual duration: " + df["duration_us"].astype(str)
    )
    fig = px.timeline(
        df,
        x_start="start",
        x_end="end_visual",
        y="operand",
        color="operand",
        hover_data={"hover": True},
        title=f"Timeline of File Operations {proc} : {', '.join(oprds)}",
    )
    fig.update_yaxes(title="Operand")
    fig.update_xaxes(title="Time")
    if not events_df.empty:
        for idx, row in events_df.iterrows():
            ts = row["timestamp"]
            label = row["event"]
            fig.add_vline(
                x=ts, line_width=1, line_dash="dash", line_color="red",
            )
            fig.add_annotation(
                x=ts,
                y=1.02 if idx % 2 == 0 else 1.03,
                xref="x", yref="paper",
                showarrow=False,
                text=label,
                font=dict(size=10)
            )
    fig.update_layout(height=1000)
    return fig

def latency_plot(proc, keyword, oprds):
    dfs = []
    for op in oprds:
        path = f"{LOGS}/{proc}/{op}.jsonl"
        df = pair_events_latency(path, keyword, op)
        if not df.empty: dfs.append(df)
    if not dfs:
        return px.scatter(title="No matching data!")
    df = pd.concat(dfs, ignore_index=True)
    if df.empty or df["latency_ms"].empty:
        return px.scatter(title="No matching data!")

    bbins = bayesian_blocks(df["latency_ms"].values)
    xbins = dict(start=float(bbins[0]), end=float(bbins[-1]), size=None)
    fig = px.histogram(
        df, x="latency_ms", color="operand",
        title=f"Latency Distribution for {proc} : {', '.join(oprds)}",
        labels={"latency_ms": "Latency (ms)", "operand": "Operand"},
        opacity=0.6
    )
    fig.update_traces(xbins=xbins, autobinx=False)
    fig.update_yaxes(type="log")
    fig.update_layout(bargap=0.05, height=1000)
    return fig

def files_plot(proc, keyword, oprds):
    all_data = []
    for op in oprds:
        path = f"{LOGS}/{proc}/{op}.jsonl"
        data = pair_events_files(path, keyword)
        if not data.empty: all_data.append(data)
    if not all_data:
        return px.scatter(title="No matching data!")
    df = pd.concat(all_data, ignore_index=True)
    if df.empty:
        return px.scatter(title="No matching data!")
    # Count operations per filename+operand
    counts = df.groupby(["fname", "operand"]).size().reset_index(name="count")
    totals = counts.groupby("fname")["count"].sum().sort_values(ascending=False)
    top_n = min(100, len(totals))
    top_files = totals.head(top_n).index
    counts = counts[counts["fname"].isin(top_files)]
    totals = totals.loc[top_files]
    counts["sort_key"] = counts["fname"].map(totals)
    counts = counts.sort_values("sort_key", ascending=False)
    fig = px.bar(
        counts, x="fname", y="count",
        color="operand", barmode="group",
        title=f"Top {top_n} Most Accessed Files by Operands {', '.join(oprds)}"
    )
    fig.update_layout(
        xaxis_title="File",
        yaxis_title="Count",
        xaxis_tickangle=-45,
        bargap=0.25,
        legend_title="Operand",
        height=1000,
    )
    return fig

# --------------
# DCC UI
app = Dash(__name__)

app.layout = html.Div([
    html.H2("I/O Profiling Dashboard"),
    dcc.Tabs(id="plot-tabs", value='timeline', children=[
        dcc.Tab(label='Timeline', value='timeline'),
        dcc.Tab(label='Latency', value='latency'),
        dcc.Tab(label='Files', value='files'),
    ]),
    html.Div([
        html.Label("PROC:"),
        dcc.Input(id='proc', value=DEFAULT_PROC, type='text'),
        html.Label("KEYWORD:"),
        dcc.Input(id='keyword', value=DEFAULT_KEYWORD, type='text'),
        html.Label("OPERANDS:"),
        dcc.Dropdown(
            id='operands',
            options=[{'label': x, 'value': x} for x in DEFAULT_OPRDS],
            value=DEFAULT_OPRDS,
            multi=True,
        ),
        html.Button('Update Plot', id='plot-btn', n_clicks=0),
    ], style={"margin":"16px 0"}),
    dcc.Loading(
        dcc.Graph(id='main-plot', style={"height":"700px"})
    ),
], style={"width":"90%","margin":"auto"})

@app.callback(
    Output('main-plot', 'figure'),
    Input('plot-btn', 'n_clicks'),
    State('plot-tabs', 'value'),
    State('proc', 'value'),
    State('keyword', 'value'),
    State('operands', 'value'),
)
def update_plot(n_clicks, tab, proc, keyword, oprds):
    if not proc or not oprds:
        return px.scatter(title="Missing input parameter(s)!")
    if tab == "timeline":
        return timeline_plot(proc, keyword, oprds)
    elif tab == "latency":
        return latency_plot(proc, keyword, oprds)
    elif tab == "files":
        return files_plot(proc, keyword, oprds)
    else:
        return px.scatter(title="Unknown plot type")

if __name__ == "__main__":
    app.run(debug=True)

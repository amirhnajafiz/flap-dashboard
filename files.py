import json
import pandas as pd
import plotly.express as px



LOGS = "logs/procs"
PROC = "vllm"
OPRD = "read"

def load_logs(path):
    for line in open(path):
        yield json.loads(line)

def pair_events(path):
    """
    Return a dataframe with:
        - fname
        - operand
        - latency_us
    """
    pending = {}
    rows = []

    for ev in load_logs(path):

        key = (ev["tid"], ev["operand"], ev["details"]["fd"])

        if ev["event_type"] == "ENTER":
            pending[key] = ev
            continue

        if ev["event_type"] == "EXIT" and key in pending:
            enter = pending.pop(key)

            rows.append({
                "fname": ev["details"]["fname"],
                "operand": ev["operand"],
                "latency_us": int(ev["details"]["latency"]) / 1000.0,  # convert ns → µs
            })

    return pd.DataFrame(rows)

def plot_file_distribution(df, top_n=30):
    """
    df must contain:
        - fname
        - operand
    """

    # Count operations per filename+operand
    counts = (
        df.groupby(["fname", "operand"])
          .size()
          .reset_index(name="count")
    )

    # Compute total counts per file for sorting
    totals = (
        counts.groupby("fname")["count"]
              .sum()
              .sort_values(ascending=False)
    )

    # Get top N filenames
    if top_n is not None:
        top_files = totals.head(top_n).index
        counts = counts[counts["fname"].isin(top_files)]
        totals = totals.loc[top_files]

    # Sort counts dataframe so bars appear ordered
    counts["sort_key"] = counts["fname"].map(totals)
    counts = counts.sort_values("sort_key", ascending=False)

    fig = px.bar(
        counts,
        x="fname",
        y="count",
        color="operand",
        barmode="group",
        title=f"Top {top_n} Most Accessed Files by Operand",
    )

    # Make labels readable
    fig.update_layout(
        xaxis_title="File",
        yaxis_title="Count",
        xaxis_tickangle=-45,
        bargap=0.25,
        legend_title="Operand",
        height=600,
    )

    fig.show()


def main():
    df = pair_events(f"{LOGS}/{PROC}/{OPRD}.jsonl")
    plot_file_distribution(df)

if __name__ == "__main__":
    main()

# file: script.py
from functools import reduce
import re
import sys
import pandas as pd



# gloal vars
LOGFILE_PATH = [
    "logs/read_bytes.txt",
    "logs/write_bytes.txt",
    "logs/read_times.txt",
    "logs/write_times.txt",
    "logs/read_counts.txt",
    "logs/write_counts.txt",
]
TOPNQ = 500

# regex patterns
RGX_PTRN = "@(\w+)\[(.+?)\]:\s*(\d+)"

def df_from_logfile(logfile_path: str) -> pd.DataFrame:
    """get a logfile and convert it into a 3-dimention pandas dataframe"""
    print(f'loading file {logfile_path}...')

    data = []
    name = ""
    with open(logfile_path, "r") as file:
        for line in file:
            # input line = "@metric[file]: value"
            # output line = [(metric, file, value)]
            split_line = re.findall(RGX_PTRN, line)
            # this pattern exists once per each line
            if len(split_line) > 0:
                index = split_line[0]

                file_name = index[1]
                metric_name = index[0]
                name = metric_name
                metric_value = int(index[2])

                # skip unnamed files
                if len(file_name) > 0:
                    data.append({
                        "file": file_name,
                        metric_name: metric_value,
                    })

    # convert to pandas dataframe to perform operations
    df = pd.DataFrame(data)
    return df.groupby('file', as_index=False)[name].sum()

def main():
    # convert all log files to pandas dataframe
    dfs = [df_from_logfile(x) for x in LOGFILE_PATH]
    # merge all dataframes based on file key
    df = reduce(lambda left, right: pd.merge(left, right, on='file'), dfs)

    # convert bytes to MB, nanoseconds to milliseconds
    df['read_bytes'] = df['read_bytes'] / (1024 * 1024)   # bytes to MB
    df['write_bytes'] = df['write_bytes'] / (1024 * 1024)
    df['read_time'] = df['read_time'] / 1_000_000         # ns to ms
    df['write_time'] = df['write_time'] / 1_000_000
    df = df.round(2)

    # rename the headers
    columns={'read_bytes': 'reads (Mb)', 'write_bytes': 'writes (Mb)', 'write_time': 'writes (ms)', 'read_time': 'reads (ms)', 'read_count': 'reads', 'write_count': 'writes'}

    ######## queries ########
    # top files that where used by read (time)
    top_read_called = df.nlargest(TOPNQ, "read_time").rename(columns=columns)
    top_read_called.to_csv("datasets/top_read_times.csv", index=False)
    
    # top files that where used by write (time)
    top_write_called = df.nlargest(TOPNQ, "write_time").rename(columns=columns)
    top_write_called.to_csv("datasets/top_write_times.csv", index=False)

    # top large files that where used for read
    top_read_bytes = df.nlargest(TOPNQ, "read_bytes").rename(columns=columns)
    top_read_bytes.to_csv("datasets/top_read_bytes.csv", index=False)

    # top large files that where used for write
    top_write_bytes = df.nlargest(TOPNQ, "write_bytes").rename(columns=columns)
    top_write_bytes.to_csv("datasets/top_write_bytes.csv", index=False)

    # top files that where used by read (count)
    top_read_counts = df.nlargest(TOPNQ, "read_count").rename(columns=columns)
    top_read_counts.to_csv("datasets/top_read_counts.csv", index=False)

    # top files that where used by write (count)
    top_write_counts = df.nlargest(TOPNQ, "write_count").rename(columns=columns)
    top_write_counts.to_csv("datasets/top_write_counts.csv", index=False)

    # total operations
    totals = df.sum(numeric_only=True).to_frame().T  # ← convert Series → single-row DataFrame
    totals = totals.round(2).reset_index(drop=True)
    totals = totals.rename(columns=columns)
    totals.to_csv("datasets/totals.csv", index=False)

if __name__ == "__main__":
    main()
    sys.exit(0)

from src.database.models import BaseModel, MetaLog
from src.logreaders import Reader


class MetaReader(Reader):
    """Meta reader reads and records meta logs from `meta_logs.txt`."""

    def name(self) -> str:
        return "meta"

    def log_file_pattern(self) -> str:
        return "trace_io_*.log"

    def make_key(self, obj: dict) -> tuple:
        return (obj["pid"], obj["tid"])

    def build_record(self, en_obj: dict, ex_obj: dict) -> BaseModel:
        ret = int(ex_obj["spec"].get("ret", -1))
        if ret < 0:
            return None

        return MetaLog(
            en_timestamp=int(en_obj["timestamp"]),
            en_datetime=en_obj["datetime"].isoformat(" "),
            ex_timestamp=int(ex_obj["timestamp"]),
            ex_datetime=ex_obj["datetime"].isoformat(" "),
            latency=(ex_obj["datetime"] - en_obj["datetime"]).total_seconds() * 1e9,
            pid=en_obj["pid"],
            tid=en_obj["tid"],
            proc=en_obj["proc"],
            event_name=en_obj["operand"],
            fname=en_obj["spec"].get("fname", "unknown"),
            ret=ret,
        )

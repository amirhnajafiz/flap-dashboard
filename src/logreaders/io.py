from src.database.models import BaseModel, IOLog
from src.logreaders import Reader


class IOReader(Reader):
    """IO reader reads and records io logs from `io_logs.txt`."""

    def name(self) -> str:
        return "io"

    def log_file_pattern(self) -> str:
        return "trace_io_*.log"

    def make_key(self, obj: dict) -> tuple:
        return (obj["pid"], obj["tid"])

    def build_record(self, en_obj: dict, ex_obj: dict) -> BaseModel:
        fd = int(en_obj["spec"].get("fd", -1))
        ret = int(ex_obj["spec"].get("ret", -1))

        if fd < 0 or ret < 0:
            return None

        return IOLog(
            en_timestamp=int(en_obj["timestamp"]),
            en_datetime=en_obj["datetime"].isoformat(" "),
            ex_timestamp=int(ex_obj["timestamp"]),
            ex_datetime=ex_obj["datetime"].isoformat(" "),
            latency=(ex_obj["datetime"] - en_obj["datetime"]).total_seconds() * 1e9,
            pid=en_obj["pid"],
            tid=en_obj["tid"],
            proc=en_obj["proc"],
            event_name=en_obj["operand"],
            fd=fd,
            ret=ret,
            countbytes=int(en_obj["spec"].get("count", 0)),
        )

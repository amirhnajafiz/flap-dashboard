from src.database.models import BaseModel, MetaLog
from src.logreaders import Reader


class MetaReader(Reader):
    """Meta reader reads and records meta logs from `trace_meta`."""

    def name(self) -> str:
        return "meta"

    def log_file_pattern(self) -> str:
        return "trace_meta_*.log"

    def build_record(self, obj: dict) -> BaseModel:
        # form the key
        key = (obj["pid"], obj["tid"])

        # map the EN to EX objects
        if obj["status"] == "EN":
            self.memory[key] = obj
            return None

        # drop none existing ones
        if key not in self.memory:
            return None

        # get both start and end events
        en_obj = self.memory.pop(key)
        ex_obj = obj

        # check the return status
        ret = int(ex_obj["spec"].get("ret", -1))
        if ret < 0:
            return None

        # return a MetaLog entry
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

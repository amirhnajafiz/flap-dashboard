from src.database.models import BaseModel, IOLog
from src.logreaders import Reader


class IOReader(Reader):
    """IO reader reads and records io logs from `trace_io`."""

    def name(self) -> str:
        return "io"

    def log_file_pattern(self) -> str:
        return "trace_io_*.log"

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

        # check the fd and ret
        fd = int(en_obj["spec"].get("fd", -1))
        ret = int(ex_obj["spec"].get("ret", -1))

        if fd < 0 or ret < 0:
            return None

        # return an IOLog entry
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

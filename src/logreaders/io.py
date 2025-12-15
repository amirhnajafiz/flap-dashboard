import logging
from pathlib import Path

from src.database.models import IOLog
from src.logreaders import Reader


class IOReader(Reader):
    """IO reader reads and records io logs from `io_logs.txt`."""

    def name(self) -> str:
        return "io"

    def get_log_files(self) -> list[str]:
        root = Path(self.dir_path)
        return [x for x in root.rglob("trace_io_*.log")]

    def start(self) -> bool:
        hashmap = {}  # map to merge log events
        batch = []  # a list to store IO logs in batch

        # reader params
        files = self.get_log_files()

        logging.debug(f"reader {self.name()}: files={len(files)}")

        for filepath in files:
            logging.debug(f"reader {self.name()} is reading {filepath}")

            limit = self.batch_size

            # read the logs line by line
            with open(filepath, "r") as file:
                for line in file:
                    # read the line
                    m = self.match_string(line)
                    if not m:
                        continue

                    # convert it into an object
                    obj = self.parse_match_into_dictionary(m)

                    # form the key
                    key = (obj["pid"], obj["tid"])

                    if obj["status"] == "EN":
                        hashmap[key] = obj
                    elif key in hashmap:
                        en_obj = hashmap[key]
                        del hashmap[key]

                        fd = int(en_obj["spec"].get("fd", -1))
                        ret = int(obj["spec"].get("ret", -1))

                        # exclude the negative records
                        if fd > -1 and ret > -1:
                            batch.append(
                                IOLog(
                                    en_timestamp=int(en_obj["timestamp"]),
                                    en_datetime=en_obj["datetime"].isoformat(" "),
                                    ex_timestamp=int(obj["timestamp"]),
                                    ex_datetime=obj["datetime"].isoformat(" "),
                                    latency=(
                                        obj["datetime"] - en_obj["datetime"]
                                    ).total_seconds()
                                    * (10**9),
                                    pid=obj["pid"],
                                    tid=obj["tid"],
                                    proc=obj["proc"],
                                    event_name=obj["operand"],
                                    fd=fd,
                                    ret=ret,
                                    countbytes=int(en_obj["spec"].get("count", 0)),
                                )
                            )

                    if len(batch) > limit:
                        self.db.batch_insert(batch)
                        batch = []

            if len(batch) > 0:
                self.db.batch_insert(batch)

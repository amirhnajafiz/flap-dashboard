import logging

from src.database.models import IOLog
from src.logreaders import Reader
from src.utils.files import list_files_by_regex


class IOReader(Reader):
    """IO reader reads and records io logs from `io_logs.txt`."""

    def name(self) -> str:
        return "io"

    def start(self) -> bool:
        # variables to store logs and insert in batch
        hashmap = {}
        batch = []
        limit = self.batch_size

        # list the log files related to this logreader
        files = list_files_by_regex(self.dir_path, "trace_io_*.log")

        logging.debug(f"reader {self.name()}: files={len(files)}")

        for filepath in files:
            logging.debug(f"reader {self.name()} is reading {filepath}")

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

                    # map the EN to EX objects
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

        # final flush of the batched records
        if len(batch) > 0:
            self.db.batch_insert(batch)

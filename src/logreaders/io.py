import os

from src.database.models import IOLog
from src.logreaders import Reader


class IOReader(Reader):
    """IO reader reads and records io logs from `io_logs.txt`."""

    def name(self) -> str:
        return "io"

    def start(self) -> bool:
        hashmap = {}  # map to merge log events
        batch = []  # a list to store IO logs in batch

        # reader params
        filepath = os.path.join(self.dir_path, "io_logs.txt")
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
                                en_datetime=en_obj["datetime"],
                                ex_timestamp=int(obj["timestamp"]),
                                ex_datetime=obj["datetime"],
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

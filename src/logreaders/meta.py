import os

from src.database.models import MetaLog
from src.logreaders import Reader


class MetaReader(Reader):
    """Meta reader reads and records meta logs from `meta_logs.txt`."""

    def name(self) -> str:
        return "meta"

    def start(self) -> bool:
        hashmap = {}  # map to merge log events
        batch = []  # a list to store logs in batch

        # reader params
        filepath = os.path.join(self.dir_path, "meta_logs.txt")
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

                    ret = int(obj["spec"].get("ret", -1))

                    # exclude the negative records
                    if ret > -1:
                        batch.append(
                            MetaLog(
                                en_timestamp=int(en_obj["timestamp"]),
                                en_datetime=en_obj["datetime"],
                                ex_timestamp=int(obj["timestamp"]),
                                ex_datetime=obj["datetime"],
                                pid=obj["pid"],
                                tid=obj["tid"],
                                proc=obj["proc"],
                                event_name=obj["operand"],
                                fname=en_obj["spec"].get("fname", "unknown"),
                                ret=ret,
                            )
                        )

                if len(batch) > limit:
                    self.db.batch_insert(batch)
                    batch = []

        if len(batch) > 0:
            self.db.batch_insert(batch)

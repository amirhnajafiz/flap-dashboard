import os

from src.logreaders import Reader


class MetaReader(Reader):
    """Meta reader reads and records meta logs from `meta_logs.txt`."""

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

                    batch.append(
                        (
                            int(en_obj["timestamp"]),
                            en_obj["datetime"],
                            int(obj["timestamp"]),
                            obj["datetime"],
                            obj["pid"],
                            obj["tid"],
                            obj["proc"],
                            obj["operand"],
                            en_obj["spec"].get("fname", ""),
                            obj["spec"].get("ret", -1),
                        )
                    )

                if len(batch) > limit:
                    self.db.insert_records(batch, "meta")
                    batch = []

        if len(batch) > 0:
            self.db.insert_records(batch, "meta")

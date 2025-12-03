import os

from src.logreaders import Reader


class MetaReader(Reader):
    def start(self) -> bool:
        hashmap = {}
        batch = []
        limit = 20

        with open(os.path.join(self.dir_path, "meta_logs.txt"), "r") as file:
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
                        del(hashmap[key])

                        batch.append((
                            int(en_obj["timestamp"]),
                            en_obj["datetime"],
                            int(obj["timestamp"]),
                            obj["datetime"],
                            obj["pid"],
                            obj["tid"],
                            obj["proc"],
                            obj["operand"],
                            "meta",
                            en_obj["spec"] + " " + obj["spec"]
                        ))

                if len(batch) > limit:
                    self.db.insert_records(batch)
                    batch = []
        
        if len(batch) > 0:
            self.db.insert_records(batch)

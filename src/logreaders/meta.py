import json
import os

from src.logreaders import Reader


class MetaReader(Reader):
    def start(self) -> bool:
        hashmap = {}
        with open(os.path.join(self.dir_path, "meta_logs.txt"), "r") as file:
            for line in file:
                # read the line
                m = self.match_string(line)
                if not m:
                    continue

                # convert it into an object
                obj = self.parse_into_object(m, self.mono, self.wall)

                # form the key
                key = (obj{""})

                if obj["status"] == "EN":
                    hashmap[]
                else:


                print(json.dumps(obj, indent=4))

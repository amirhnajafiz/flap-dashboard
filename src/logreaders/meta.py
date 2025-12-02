import json
import os

from src.logreaders import Reader
from src.rexfsm import match_string, parse_into_object


class MetaReader(Reader):
    def start(self) -> bool:
        with open(os.path.join(self.dir_path, "meta_logs.txt"), "r") as file:
            for line in file:
                m = match_string(line)
                if not m:
                    continue

                obj = parse_into_object(m, self.mono, self.wall)

                print(json.dumps(obj, indent=4))

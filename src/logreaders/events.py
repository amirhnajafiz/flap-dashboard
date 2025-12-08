import json
import os

from src.logreaders import Reader


class EventsReader(Reader):
    def name(self) -> str:
        return "events"

    def start(self) -> bool:
        with open(os.path.join(self.dir_path, "event_logs.txt"), "r") as file:
            for line in file:
                m = self.match_string(line)
                if not m:
                    continue

                obj = self.parse_into_object(m, self.mono, self.wall)

                print(json.dumps(obj, indent=4))

import re
from src.time_reference import datetime_from_nanos

regex = re.compile(
    r"^(?P<time>\d+)\s+"
    r"\{pid=(?P<pid>\d+)\s+tid=(?P<tid>\d+)\s+proc=(?P<proc>[^}]+)\}"
    r"\{(?P<status>EN|EX)\s+(?P<operand>[a-zA-Z0-9_]+)\}"
    r"\{(?P<spec>[^}]*)\}$"
)


def match_string(input: str) -> re.Match:
    return regex.match(input)

def parse_into_object(m: str, mono: float, wall: float) -> dict:
    meta = {
                "time": m.group("time"),
                "datetime": datetime_from_nanos(
                    mono=mono, wall=wall, input=int(m.group("time"))
                ).isoformat(" "),
                "pid": m.group("pid"),
                "tid": m.group("tid"),
                "proc": m.group("proc"),
            }

    status = m.group("status")
    operand = m.group("operand")

    spec_str = m.group("spec")
    spec = {}
    if spec_str.strip():
        for item in spec_str.split():
            k, v = item.split("=", 1)
            spec[k] = v

    return {"meta": meta, "status": status, "operand": operand, "spec": spec}
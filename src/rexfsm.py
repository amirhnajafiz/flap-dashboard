import re

regex = re.compile(
    r"^(?P<time>\d+)\s+"
    r"\{pid=(?P<pid>\d+)\s+tid=(?P<tid>\d+)\s+proc=(?P<proc>[^}]+)\}"
    r"\{(?P<status>EN|EX)\s+(?P<operand>[a-zA-Z0-9_]+)\}"
    r"\{(?P<spec>[^}]*)\}$"
)


def match_string(input: str) -> re.Match:
    return regex.match(input)

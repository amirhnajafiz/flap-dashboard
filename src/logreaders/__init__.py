import datetime
import re
from abc import ABC


class Reader(ABC):
    """Reader is an abstract class for all types of log readers.
    A log reader is a class which is responsible for reading an specific type
    of log file, parse it line by line, and insert it into the database.
    """

    def __init__(self, dir_path: str, mono: float, wall: float):
        """The constructor method accepts parameters needed for a general
        log reader instance.

        :param dir_path: each log reader needs to know where to look for its log file
        :param reference mono: timestamp based on a monotonic clock, offset by a known “reference” point
        :param reference wall: real-world timestamp that serves as the anchor for converting other timestamps
        """
        self.dir_path = dir_path

        self.__ref_mono_ns = mono * 1e9
        self.__ref_wall_ns = wall * 1e9
        self.__regex = re.compile(
            r"^(?P<time>\d+)\s+"
            r"\{pid=(?P<pid>\d+)\s+tid=(?P<tid>\d+)\s+proc=(?P<proc>[^}]+)\}"
            r"\{(?P<status>EN|EX)\s+(?P<operand>[a-zA-Z0-9_]+)\}"
            r"\{(?P<spec>[^}]*)\}$"
        )

    def convert_monotonic_time_to_datetime(self, input: float) -> datetime.datetime:
        """Using time references to convert a monotonic time to python datatime object.
        (timestamp = monotonic_time + boot_reference_time)

        :param input: monotonic time in nanoseconds
        :raturn datetime.datetime: datetime object of the monotonic time
        """

        # convert monotonic ns to wall-clock ns
        wall_ns = self.__ref_wall_ns + (input - self.__ref_mono_ns)

        # convert to Python datetime
        dt = datetime.datetime.fromtimestamp(wall_ns / 1e9)

        return dt

    def match_string(self, input: str) -> re.Match:
        """Using Regex final state machine to process a log entry.
        (input format: 1648212592899378 {pid=13030 tid=13140 proc=prometheus}{EN page_fault_user}{addr=824945852416})

        :param input: input string
        :return re.Match: a regex fsm output
        """
        return self.__regex.match(input)

    def parse_match_into_dictionary(self, match: re.Match) -> dict:
        """Parse input re.Match object into a dictionary.

        :param match: a not-none match object
        :raturn dict: python dictionary (meta: map[stirng]string, status: EN|EX, operand, spec: map[string]string)
        """

        # extract the meta output
        meta = {
            "timestamp": match.group("time"),
            "datetime": self.convert_monotonic_time_to_datetime(
                input=float(match.group("time"))
            ).isoformat(" "),
            "pid": match.group("pid"),
            "tid": match.group("tid"),
            "proc": match.group("proc"),
        }

        # extract the status and operand
        status = match.group("status")
        operand = match.group("operand")

        # extract spec key-values
        spec_str = match.group("spec")
        spec = {}
        if spec_str.strip():
            for item in spec_str.split():
                k, v = item.split("=", 1)
                spec[k] = v

        return {"meta": meta, "status": status, "operand": operand, "spec": spec}

    @classmethod
    def start(self) -> tuple[bool, str]:
        """Start log processing.

        :return bool: true if any error happens
        :return str: the error message
        """
        pass

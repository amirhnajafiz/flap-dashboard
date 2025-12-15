import datetime
import logging
import re
from abc import ABC

from src.database import BaseModel, Database
from src.utils.files import list_files_by_regex


class Reader(ABC):
    """Reader is an abstract class for all types of log readers.
    A log reader is a class which is responsible for reading an specific type
    of log file, parse it line by line, and insert it into the database.
    """

    def __init__(
        self,
        dir_path: str,
        mono: float,
        wall: float,
        db: Database,
        batch_size: int,
    ):
        """The constructor method accepts parameters needed for a general
        log reader instance.

        :param dir_path: each log reader needs to know where to look for its log file
        :param reference mono: timestamp based on a monotonic clock, offset by a known “reference” point
        :param reference wall: real-world timestamp that serves as the anchor for converting other timestamps
        :param batch_size: the batch size to insert log records
        """
        self.dir_path = dir_path
        self.batch_size = batch_size
        self.db = db
        self.memory = {}

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

        # parse spec field into dictionary
        spec_str = match.group("spec")
        spec = {}
        if spec_str.strip():
            for item in spec_str.split():
                try:
                    k, v = item.split("=", 1)
                    spec[k] = v
                except ValueError:
                    continue

        return {
            "timestamp": match.group("time"),
            "datetime": self.convert_monotonic_time_to_datetime(
                input=float(match.group("time"))
            ),
            "pid": match.group("pid"),
            "tid": match.group("tid"),
            "proc": match.group("proc"),
            "status": match.group("status"),
            "operand": match.group("operand"),
            "spec": spec,
        }

    def start(self):
        """Start log processing."""
        # variables to store logs and insert in batch
        batch = []
        limit = self.batch_size

        # list the log files related to this logreader
        files = list_files_by_regex(self.dir_path, self.log_file_pattern())

        logging.debug(f"reader {self.name()}: files={len(files)}")

        # loop over files and read them
        for filepath in files:
            logging.debug(f"reader {self.name()} is reading {filepath}")

            # read the logs line by line
            with open(filepath, "r") as file:
                for line in file:
                    # read the line
                    m = self.match_string(line)
                    if not m:
                        continue

                    # convert it into an object
                    obj = self.parse_match_into_dictionary(m)

                    # call build record and if any records return, add them into the batch
                    record = self.build_record(obj)
                    if record is not None:
                        batch.append(record)

                    # flush batched records
                    if len(batch) > limit:
                        self.db.batch_insert(batch)
                        batch = []

        # final flush of the batched records
        if len(batch) > 0:
            self.db.batch_insert(batch)

    @classmethod
    def name(self) -> str:
        """Return the name of reader instance."""
        pass

    @classmethod
    def log_file_pattern(self) -> str:
        """Return the reader log file names pattern.

        :return str: the regex
        """
        pass

    @classmethod
    def build_record(self, obj: dict) -> BaseModel:
        """Create a record from the given object.

        :param obj: input object
        :return BaseModel: a database model
        """
        pass

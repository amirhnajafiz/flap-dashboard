from sqlalchemy import BigInteger, Column, Index, Integer, String, Text

from src.database import AsDictMixin, BaseModel


class MetaLog(BaseModel, AsDictMixin):
    """A meta log model stores information about a meta entry.
    these logs will be used to provide useful details for io events.
    """

    __tablename__ = "meta_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    en_timestamp = Column(BigInteger)
    en_datetime = Column(Text)
    ex_timestamp = Column(BigInteger)
    ex_datetime = Column(Text)
    latency = Column(BigInteger)

    pid = Column(Integer)
    tid = Column(Integer)
    proc = Column(String)
    event_name = Column(String)
    fname = Column(String)
    ret = Column(Integer)

    __table_args__ = (Index("idx_meta_proc_ret_ts", "proc", "ret", "en_timestamp"),)


class IOLog(BaseModel, AsDictMixin):
    """An IO log model is used to replay the target application io operations."""

    __tablename__ = "io_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    en_timestamp = Column(BigInteger)
    en_datetime = Column(Text)
    ex_timestamp = Column(BigInteger)
    ex_datetime = Column(BigInteger)
    latency = Column(BigInteger)

    pid = Column(Integer)
    tid = Column(Integer)
    proc = Column(String)
    event_name = Column(String)

    fd = Column(Integer)
    ret = Column(Integer)
    countbytes = Column(Integer)
    fname = Column(Text)

    __table_args__ = (Index("idx_io_proc_fd_ts", "proc", "fd", "en_timestamp"),)


class MemoryLog(BaseModel, AsDictMixin):
    """A Memory log model is used to replay the memory events."""

    __tablename__ = "memory_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    en_timestamp = Column(BigInteger)
    en_datetime = Column(Text)
    ex_timestamp = Column(BigInteger)
    ex_datetime = Column(BigInteger)
    latency = Column(BigInteger)

    pid = Column(Integer)
    tid = Column(Integer)
    proc = Column(String)
    event_name = Column(String)

    fd = Column(Integer)
    ret = Column(Integer)

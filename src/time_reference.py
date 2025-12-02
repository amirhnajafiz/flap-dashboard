import datetime


def generate_datetime_from_nanos(
    mono: float, wall: float, input: float
) -> datetime.datetime:
    """Accept the mono and wall in nanoseconds and convert the input from nanoseconds to datetime object.

    :param mono:
    :param wall:
    :param input:
    :return datetime.datetime:
    """
    ref_mono_ns = mono * 1e9
    ref_wall_ns = wall * 1e9

    # convert monotonic ns to wall-clock ns
    wall_ns = ref_wall_ns + (input - ref_mono_ns)

    # convert to Python datetime
    dt = datetime.datetime.fromtimestamp(wall_ns / 1e9)

    return dt

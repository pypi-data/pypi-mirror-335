import time


__all__ = ["int_time"]


def int_time() -> int:
    return int(time.time() * 1E3)

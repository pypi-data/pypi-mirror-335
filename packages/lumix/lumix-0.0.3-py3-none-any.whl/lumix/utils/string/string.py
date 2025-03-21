import random
import string


__all__ = [
    "random_string"
]


def random_string(length: int = 10) -> str:
    """"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

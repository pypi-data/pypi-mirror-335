from typing import Protocol


class DateTimeLike(Protocol):
    def isoformat(self) -> str: ...  # noqa: E704


def date_handler(obj: DateTimeLike) -> str:
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    else:
        raise TypeError("Unserializable object {} of type {}".format(obj, type(obj)))

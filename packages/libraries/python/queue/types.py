from typing import TypeAlias, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .queue import Queue

JsonValue: TypeAlias = (
    str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
)

QueueFactory = Callable[[str], "Queue"]

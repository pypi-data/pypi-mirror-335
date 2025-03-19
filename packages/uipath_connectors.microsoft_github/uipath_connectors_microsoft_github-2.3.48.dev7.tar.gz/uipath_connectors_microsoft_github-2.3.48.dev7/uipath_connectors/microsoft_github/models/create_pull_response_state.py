from enum import Enum


class CreatePullResponseState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"

    def __str__(self) -> str:
        return str(self.value)

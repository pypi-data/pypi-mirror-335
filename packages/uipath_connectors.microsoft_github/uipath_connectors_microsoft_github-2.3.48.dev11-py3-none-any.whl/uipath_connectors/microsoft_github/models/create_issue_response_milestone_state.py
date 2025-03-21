from enum import Enum


class CreateIssueResponseMilestoneState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"

    def __str__(self) -> str:
        return str(self.value)

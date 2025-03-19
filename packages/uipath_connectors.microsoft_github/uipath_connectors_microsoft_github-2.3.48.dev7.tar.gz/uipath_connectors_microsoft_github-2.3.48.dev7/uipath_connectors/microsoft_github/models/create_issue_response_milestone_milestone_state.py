from enum import Enum


class CreateIssueResponseMilestoneMilestoneState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"

    def __str__(self) -> str:
        return str(self.value)

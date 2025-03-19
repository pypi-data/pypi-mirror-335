from enum import Enum


class SearchIssuesMilestoneMilestoneState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"

    def __str__(self) -> str:
        return str(self.value)

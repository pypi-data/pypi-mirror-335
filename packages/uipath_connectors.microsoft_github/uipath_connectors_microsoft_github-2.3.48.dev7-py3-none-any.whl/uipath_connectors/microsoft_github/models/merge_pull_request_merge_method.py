from enum import Enum


class MergePullRequestMergeMethod(str, Enum):
    MERGE = "merge"
    REBASE = "rebase"
    SQUASH = "squash"

    def __str__(self) -> str:
        return str(self.value)

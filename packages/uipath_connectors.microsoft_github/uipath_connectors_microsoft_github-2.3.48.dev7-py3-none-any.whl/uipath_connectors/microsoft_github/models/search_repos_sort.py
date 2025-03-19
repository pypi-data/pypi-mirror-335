from enum import Enum


class SearchReposSort(str, Enum):
    FORKS = "forks"
    HELP_WANTED_ISSUES = "help-wanted-issues"
    STARS = "stars"
    UPDATED = "updated"

    def __str__(self) -> str:
        return str(self.value)

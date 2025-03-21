from enum import Enum


class UpdateIssueResponseAuthorAssociation(str, Enum):
    COLLABORATOR = "COLLABORATOR"
    CONTRIBUTOR = "CONTRIBUTOR"
    FIRSTTIMECONTRIBUTOR = "FIRST_TIME_CONTRIBUTOR"
    FIRSTTIMER = "FIRST_TIMER"
    MANNEQUIN = "MANNEQUIN"
    MEMBER = "MEMBER"
    NONE = "NONE"
    OWNER = "OWNER"

    def __str__(self) -> str:
        return str(self.value)

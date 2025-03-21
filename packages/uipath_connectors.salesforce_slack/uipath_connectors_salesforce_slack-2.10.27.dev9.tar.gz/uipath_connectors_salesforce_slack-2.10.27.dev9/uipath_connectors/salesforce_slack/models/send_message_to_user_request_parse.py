from enum import Enum


class SendMessageToUserRequestParse(str, Enum):
    FULL = "full"
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)

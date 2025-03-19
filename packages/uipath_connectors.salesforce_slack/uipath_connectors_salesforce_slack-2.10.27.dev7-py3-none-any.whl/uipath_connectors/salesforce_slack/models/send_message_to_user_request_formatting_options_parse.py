from enum import Enum


class SendMessageToUserRequestFormattingOptionsParse(str, Enum):
    FULL = "full"
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)

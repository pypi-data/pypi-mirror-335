from enum import Enum


class SendButtonResponseRequestResponseType(str, Enum):
    EPHEMERAL = "ephemeral"
    IN_CHANNEL = "in_channel"

    def __str__(self) -> str:
        return str(self.value)

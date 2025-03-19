from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.send_message_to_user_response_icons import SendMessageToUserResponseIcons
from ..models.send_message_to_user_response_response_metadata import (
    SendMessageToUserResponseResponseMetadata,
)
from ..models.send_message_to_user_response_blocks_array_item_ref import (
    SendMessageToUserResponseBlocksArrayItemRef,
)
from ..models.send_message_to_user_response_metadata import (
    SendMessageToUserResponseMetadata,
)
from ..models.send_message_to_user_response_message import (
    SendMessageToUserResponseMessage,
)
from ..models.send_message_to_user_response_root import SendMessageToUserResponseRoot


class SendMessageToUserResponse(BaseModel):
    """
    Attributes:
        app_id (Optional[str]):  Example: A02CEJTE85R.
        blocks (Optional[list['SendMessageToUserResponseBlocksArrayItemRef']]):
        channel (Optional[str]): User Example: C02CAP3LAAG.
        icons (Optional[SendMessageToUserResponseIcons]):
        message (Optional[SendMessageToUserResponseMessage]):
        metadata (Optional[SendMessageToUserResponseMetadata]):
        ok (Optional[bool]):  Example: True.
        response_metadata (Optional[SendMessageToUserResponseResponseMetadata]):
        root (Optional[SendMessageToUserResponseRoot]):
        subtype (Optional[str]):  Example: thread_broadcast.
        thread_ts (Optional[str]): The ID (timestamp) of the message sent Example: 1675217357.904929.
        ts (Optional[str]): The ID (timestamp) of the message sent Example: 1631092102.000400.
        username (Optional[str]): Bot name Example: My Bot lalitha new.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    app_id: Optional[str] = Field(alias="app_id", default=None)
    blocks: Optional[list["SendMessageToUserResponseBlocksArrayItemRef"]] = Field(
        alias="blocks", default=None
    )
    channel: Optional[str] = Field(alias="channel", default=None)
    icons: Optional["SendMessageToUserResponseIcons"] = Field(
        alias="icons", default=None
    )
    message: Optional["SendMessageToUserResponseMessage"] = Field(
        alias="message", default=None
    )
    metadata: Optional["SendMessageToUserResponseMetadata"] = Field(
        alias="metadata", default=None
    )
    ok: Optional[bool] = Field(alias="ok", default=None)
    response_metadata: Optional["SendMessageToUserResponseResponseMetadata"] = Field(
        alias="response_metadata", default=None
    )
    root: Optional["SendMessageToUserResponseRoot"] = Field(alias="root", default=None)
    subtype: Optional[str] = Field(alias="subtype", default=None)
    thread_ts: Optional[str] = Field(alias="thread_ts", default=None)
    ts: Optional[str] = Field(alias="ts", default=None)
    username: Optional[str] = Field(alias="username", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SendMessageToUserResponse"], src_dict: Dict[str, Any]):
        return cls.model_validate(src_dict)

    @property
    def additional_keys(self) -> list[str]:
        base_fields = self.model_fields.keys()
        return [k for k in self.__dict__ if k not in base_fields]

    def __getitem__(self, key: str) -> Any:
        if key in self.__dict__:
            return self.__dict__[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self.__dict__:
            del self.__dict__[key]
        else:
            raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__

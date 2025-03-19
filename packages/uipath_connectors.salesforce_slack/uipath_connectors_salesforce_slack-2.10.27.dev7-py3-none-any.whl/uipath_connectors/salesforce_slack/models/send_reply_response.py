from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.send_reply_response_metadata import SendReplyResponseMetadata
from ..models.send_reply_response_response_metadata import (
    SendReplyResponseResponseMetadata,
)
from ..models.send_reply_response_message import SendReplyResponseMessage
from ..models.send_reply_response_icons import SendReplyResponseIcons
from ..models.send_reply_response_root import SendReplyResponseRoot
from ..models.send_reply_response_blocks_array_item_ref import (
    SendReplyResponseBlocksArrayItemRef,
)


class SendReplyResponse(BaseModel):
    """
    Attributes:
        app_id (Optional[str]):  Example: A02CEJTE85R.
        blocks (Optional[list['SendReplyResponseBlocksArrayItemRef']]):
        channel (Optional[str]): Select the public or private channel from the dropdown or pass channel name or channel
                ID. Ex: demo-slack-channel1 Example: C02CAP3LAAG.
        icons (Optional[SendReplyResponseIcons]):
        message (Optional[SendReplyResponseMessage]):
        metadata (Optional[SendReplyResponseMetadata]):
        ok (Optional[bool]):  Example: True.
        response_metadata (Optional[SendReplyResponseResponseMetadata]):
        root (Optional[SendReplyResponseRoot]):
        subtype (Optional[str]):  Example: thread_broadcast.
        thread_ts (Optional[str]): Message timestamp Example: 1675217357.904929.
        ts (Optional[str]): The ID (timestamp) of the message sent Example: 1631092102.000400.
        username (Optional[str]): Bot name Example: My Bot lalitha new.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    app_id: Optional[str] = Field(alias="app_id", default=None)
    blocks: Optional[list["SendReplyResponseBlocksArrayItemRef"]] = Field(
        alias="blocks", default=None
    )
    channel: Optional[str] = Field(alias="channel", default=None)
    icons: Optional["SendReplyResponseIcons"] = Field(alias="icons", default=None)
    message: Optional["SendReplyResponseMessage"] = Field(alias="message", default=None)
    metadata: Optional["SendReplyResponseMetadata"] = Field(
        alias="metadata", default=None
    )
    ok: Optional[bool] = Field(alias="ok", default=None)
    response_metadata: Optional["SendReplyResponseResponseMetadata"] = Field(
        alias="response_metadata", default=None
    )
    root: Optional["SendReplyResponseRoot"] = Field(alias="root", default=None)
    subtype: Optional[str] = Field(alias="subtype", default=None)
    thread_ts: Optional[str] = Field(alias="thread_ts", default=None)
    ts: Optional[str] = Field(alias="ts", default=None)
    username: Optional[str] = Field(alias="username", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SendReplyResponse"], src_dict: Dict[str, Any]):
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

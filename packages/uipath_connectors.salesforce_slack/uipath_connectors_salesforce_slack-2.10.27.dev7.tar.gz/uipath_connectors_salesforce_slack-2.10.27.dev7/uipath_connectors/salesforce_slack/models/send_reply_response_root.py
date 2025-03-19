from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.send_reply_response_root_icons import SendReplyResponseRootIcons
from ..models.send_reply_response_root_blocks_array_item_ref import (
    SendReplyResponseRootBlocksArrayItemRef,
)
from ..models.send_reply_response_root_metadata import SendReplyResponseRootMetadata


class SendReplyResponseRoot(BaseModel):
    """
    Attributes:
        app_id (Optional[str]):  Example: A02CEJTE85R.
        blocks (Optional[list['SendReplyResponseRootBlocksArrayItemRef']]):
        bot_id (Optional[str]):  Example: B02DYM5F1ST.
        icons (Optional[SendReplyResponseRootIcons]):
        is_locked (Optional[bool]):
        latest_reply (Optional[str]):  Example: 1675233584.607969.
        metadata (Optional[SendReplyResponseRootMetadata]):
        reply_count (Optional[int]):  Example: 4.0.
        reply_users (Optional[list[str]]):  Example: ['B02DYM5F1ST'].
        reply_users_count (Optional[int]):  Example: 1.0.
        subscribed (Optional[bool]):
        subtype (Optional[str]):  Example: bot_message.
        text (Optional[str]):  Example: failtest.
        thread_ts (Optional[str]):  Example: 1675217357.904929.
        ts (Optional[str]):  Example: 1675217357.904929.
        type_ (Optional[str]):  Example: message.
        username (Optional[str]):  Example: UiPath for Slack Staging.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    app_id: Optional[str] = Field(alias="app_id", default=None)
    blocks: Optional[list["SendReplyResponseRootBlocksArrayItemRef"]] = Field(
        alias="blocks", default=None
    )
    bot_id: Optional[str] = Field(alias="bot_id", default=None)
    icons: Optional["SendReplyResponseRootIcons"] = Field(alias="icons", default=None)
    is_locked: Optional[bool] = Field(alias="is_locked", default=None)
    latest_reply: Optional[str] = Field(alias="latest_reply", default=None)
    metadata: Optional["SendReplyResponseRootMetadata"] = Field(
        alias="metadata", default=None
    )
    reply_count: Optional[int] = Field(alias="reply_count", default=None)
    reply_users: Optional[list[str]] = Field(alias="reply_users", default=None)
    reply_users_count: Optional[int] = Field(alias="reply_users_count", default=None)
    subscribed: Optional[bool] = Field(alias="subscribed", default=None)
    subtype: Optional[str] = Field(alias="subtype", default=None)
    text: Optional[str] = Field(alias="text", default=None)
    thread_ts: Optional[str] = Field(alias="thread_ts", default=None)
    ts: Optional[str] = Field(alias="ts", default=None)
    type_: Optional[str] = Field(alias="type", default=None)
    username: Optional[str] = Field(alias="username", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SendReplyResponseRoot"], src_dict: Dict[str, Any]):
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

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.send_reply_request_attachments_actions_array_item_ref import (
    SendReplyRequestAttachmentsActionsArrayItemRef,
)


class SendReplyRequestAttachmentsArrayItemRef(BaseModel):
    """
    Attributes:
        actions (Optional[list['SendReplyRequestAttachmentsActionsArrayItemRef']]):
        attachment_type (Optional[str]):  Example: default.
        callback_id (Optional[str]):  Example: wopr_game.
        color (Optional[str]):  Example: #3AA3E3.
        fallback (Optional[str]):  Example: You are unable to choose a game.
        text (Optional[str]):  Example: Choose a game to play.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    actions: Optional[list["SendReplyRequestAttachmentsActionsArrayItemRef"]] = Field(
        alias="actions", default=None
    )
    attachment_type: Optional[str] = Field(alias="attachment_type", default=None)
    callback_id: Optional[str] = Field(alias="callback_id", default=None)
    color: Optional[str] = Field(alias="color", default=None)
    fallback: Optional[str] = Field(alias="fallback", default=None)
    text: Optional[str] = Field(alias="text", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SendReplyRequestAttachmentsArrayItemRef"], src_dict: Dict[str, Any]
    ):
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

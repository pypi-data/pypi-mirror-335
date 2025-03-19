from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.send_message_to_user_request_formatting_options_parse import (
    SendMessageToUserRequestFormattingOptionsParse,
)
from ..models.send_message_to_user_request_metadata import (
    SendMessageToUserRequestMetadata,
)
from ..models.send_message_to_user_request_attachments_array_item_ref import (
    SendMessageToUserRequestAttachmentsArrayItemRef,
)


class SendMessageToUserRequest(BaseModel):
    """
    Attributes:
        channel (str): User Example: C02CAP3LAAG.
        message_to_send (str): The formatted text of the message to be sent. This is also the main 'block' section text
                Example: string.
        attachments (Optional[list['SendMessageToUserRequestAttachmentsArrayItemRef']]):
        buttons (Optional[str]): Buttons actions Example: string.
        fields (Optional[str]): Message fields Example: string.
        icon_emoji (Optional[str]): Bot icon
        icon_url (Optional[str]): URL to an image to use as the icon for this message Example: https://a.slack-
                edge.com/production-standard-emoji-assets/14.0/apple-medium/0032-fe0f-20e3@2x.png.
        image (Optional[str]): The URL of the secondary image attachment to be shared as part of the message. The image
                will always be at the bottom of the entire message block Example: string.
        link_names (Optional[bool]): Whether to link and mention all the user groups automatically if the respective
                names are mentioned in the text message? Example: True.
        metadata (Optional[SendMessageToUserRequestMetadata]):
        mrkdwn (Optional[bool]):  Example: True.
        parse (Optional[SendMessageToUserRequestFormattingOptionsParse]): Change how messages are treated. Pass 'none'
                for removing hyperlinks and pass 'full' to ignore slack’s default formatting Example: none.
        reply_broadcast (Optional[bool]):  Example: True.
        thread_ts (Optional[str]): The ID (timestamp) of the message sent Example: 1675217357.904929.
        unfurl_links (Optional[bool]): Whether to display the preview of the links mentioned in the text message?
                Example: True.
        unfurl_media (Optional[bool]):
        username (Optional[str]): Bot name Example: My Bot lalitha new.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    channel: str = Field(alias="channel")
    message_to_send: str = Field(alias="messageToSend")
    attachments: Optional[list["SendMessageToUserRequestAttachmentsArrayItemRef"]] = (
        Field(alias="attachments", default=None)
    )
    buttons: Optional[str] = Field(alias="buttons", default=None)
    fields: Optional[str] = Field(alias="fields", default=None)
    icon_emoji: Optional[str] = Field(alias="icon_emoji", default=None)
    icon_url: Optional[str] = Field(alias="icon_url", default=None)
    image: Optional[str] = Field(alias="image", default=None)
    link_names: Optional[bool] = Field(alias="link_names", default=None)
    metadata: Optional["SendMessageToUserRequestMetadata"] = Field(
        alias="metadata", default=None
    )
    mrkdwn: Optional[bool] = Field(alias="mrkdwn", default=None)
    parse: Optional[SendMessageToUserRequestFormattingOptionsParse] = Field(
        alias="parse", default=None
    )
    reply_broadcast: Optional[bool] = Field(alias="reply_broadcast", default=None)
    thread_ts: Optional[str] = Field(alias="thread_ts", default=None)
    unfurl_links: Optional[bool] = Field(alias="unfurl_links", default=None)
    unfurl_media: Optional[bool] = Field(alias="unfurl_media", default=None)
    username: Optional[str] = Field(alias="username", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SendMessageToUserRequest"], src_dict: Dict[str, Any]):
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

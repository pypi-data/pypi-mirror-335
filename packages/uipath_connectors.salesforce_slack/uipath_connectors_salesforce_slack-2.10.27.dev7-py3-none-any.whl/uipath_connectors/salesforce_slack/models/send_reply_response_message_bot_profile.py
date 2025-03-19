from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.send_reply_response_message_bot_profile_icons import (
    SendReplyResponseMessageBotProfileIcons,
)


class SendReplyResponseMessageBotProfile(BaseModel):
    """
    Attributes:
        app_id (Optional[str]):  Example: A44S6RJ2V.
        deleted (Optional[bool]):
        icons (Optional[SendReplyResponseMessageBotProfileIcons]):
        id (Optional[str]):  Example: B02CRAP7A23.
        name (Optional[str]):  Example: CE DEV App.
        team_id (Optional[str]):  Example: TCU0VUNLT.
        updated (Optional[int]):  Example: 1.63056859E9.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    app_id: Optional[str] = Field(alias="app_id", default=None)
    deleted: Optional[bool] = Field(alias="deleted", default=None)
    icons: Optional["SendReplyResponseMessageBotProfileIcons"] = Field(
        alias="icons", default=None
    )
    id: Optional[str] = Field(alias="id", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    team_id: Optional[str] = Field(alias="team_id", default=None)
    updated: Optional[int] = Field(alias="updated", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SendReplyResponseMessageBotProfile"], src_dict: Dict[str, Any]
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

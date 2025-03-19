from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_conversation_info_response_topic import (
    GetConversationInfoResponseTopic,
)
from ..models.get_conversation_info_response_purpose import (
    GetConversationInfoResponsePurpose,
)


class GetConversationInfoResponse(BaseModel):
    """
    Attributes:
        created (Optional[int]):  Example: 1.629792267E9.
        creator (Optional[str]):  Example: UCUFVVCKS.
        id (Optional[str]):  Example: C02C4TL46CT.
        is_archived (Optional[bool]):
        is_channel (Optional[bool]):  Example: True.
        is_ext_shared (Optional[bool]):
        is_general (Optional[bool]):
        is_group (Optional[bool]):
        is_im (Optional[bool]):
        is_member (Optional[bool]):  Example: True.
        is_mpim (Optional[bool]):
        is_org_shared (Optional[bool]):
        is_pending_ext_shared (Optional[bool]):
        is_private (Optional[bool]):
        is_shared (Optional[bool]):
        last_read (Optional[str]):  Example: 1631093304.000300.
        locale (Optional[str]):  Example: en-US.
        name (Optional[str]):  Example: periodic-test-3.
        name_normalized (Optional[str]):  Example: periodic-test-3.
        num_members (Optional[int]):  Example: 1.0.
        purpose (Optional[GetConversationInfoResponsePurpose]):
        shared_team_ids (Optional[list[str]]):  Example: ['TCU0VUNLT'].
        topic (Optional[GetConversationInfoResponseTopic]):
        unlinked (Optional[int]):  Example: 0.0.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    created: Optional[int] = Field(alias="created", default=None)
    creator: Optional[str] = Field(alias="creator", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    is_archived: Optional[bool] = Field(alias="is_archived", default=None)
    is_channel: Optional[bool] = Field(alias="is_channel", default=None)
    is_ext_shared: Optional[bool] = Field(alias="is_ext_shared", default=None)
    is_general: Optional[bool] = Field(alias="is_general", default=None)
    is_group: Optional[bool] = Field(alias="is_group", default=None)
    is_im: Optional[bool] = Field(alias="is_im", default=None)
    is_member: Optional[bool] = Field(alias="is_member", default=None)
    is_mpim: Optional[bool] = Field(alias="is_mpim", default=None)
    is_org_shared: Optional[bool] = Field(alias="is_org_shared", default=None)
    is_pending_ext_shared: Optional[bool] = Field(
        alias="is_pending_ext_shared", default=None
    )
    is_private: Optional[bool] = Field(alias="is_private", default=None)
    is_shared: Optional[bool] = Field(alias="is_shared", default=None)
    last_read: Optional[str] = Field(alias="last_read", default=None)
    locale: Optional[str] = Field(alias="locale", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    name_normalized: Optional[str] = Field(alias="name_normalized", default=None)
    num_members: Optional[int] = Field(alias="num_members", default=None)
    purpose: Optional["GetConversationInfoResponsePurpose"] = Field(
        alias="purpose", default=None
    )
    shared_team_ids: Optional[list[str]] = Field(alias="shared_team_ids", default=None)
    topic: Optional["GetConversationInfoResponseTopic"] = Field(
        alias="topic", default=None
    )
    unlinked: Optional[int] = Field(alias="unlinked", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetConversationInfoResponse"], src_dict: Dict[str, Any]):
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

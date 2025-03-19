from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_user_by_email_response_profile import GetUserByEmailResponseProfile


class GetUserByEmailResponse(BaseModel):
    """
    Attributes:
        color (Optional[str]):  Example: 9f69e7.
        deleted (Optional[bool]):
        has_2fa (Optional[bool]):
        id (Optional[str]): ID of a user Example: U01FYLMH1D3.
        is_admin (Optional[bool]):  Example: True.
        is_app_user (Optional[bool]):
        is_bot (Optional[bool]):
        is_email_confirmed (Optional[bool]):  Example: True.
        is_owner (Optional[bool]):  Example: True.
        is_primary_owner (Optional[bool]):  Example: True.
        is_restricted (Optional[bool]):
        is_ultra_restricted (Optional[bool]):
        name (Optional[str]):  Example: dhandu1995.
        profile (Optional[GetUserByEmailResponseProfile]):
        real_name (Optional[str]):  Example: dhandu1995.
        team_id (Optional[str]):  Example: T01G1P7CKR8.
        tz (Optional[str]):  Example: Asia/Kolkata.
        tz_label (Optional[str]):  Example: India Standard Time.
        tz_offset (Optional[int]):  Example: 19800.0.
        updated (Optional[int]):  Example: 1.664445309E9.
        who_can_share_contact_card (Optional[str]):  Example: EVERYONE.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    color: Optional[str] = Field(alias="color", default=None)
    deleted: Optional[bool] = Field(alias="deleted", default=None)
    has_2fa: Optional[bool] = Field(alias="has_2fa", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    is_admin: Optional[bool] = Field(alias="is_admin", default=None)
    is_app_user: Optional[bool] = Field(alias="is_app_user", default=None)
    is_bot: Optional[bool] = Field(alias="is_bot", default=None)
    is_email_confirmed: Optional[bool] = Field(alias="is_email_confirmed", default=None)
    is_owner: Optional[bool] = Field(alias="is_owner", default=None)
    is_primary_owner: Optional[bool] = Field(alias="is_primary_owner", default=None)
    is_restricted: Optional[bool] = Field(alias="is_restricted", default=None)
    is_ultra_restricted: Optional[bool] = Field(
        alias="is_ultra_restricted", default=None
    )
    name: Optional[str] = Field(alias="name", default=None)
    profile: Optional["GetUserByEmailResponseProfile"] = Field(
        alias="profile", default=None
    )
    real_name: Optional[str] = Field(alias="real_name", default=None)
    team_id: Optional[str] = Field(alias="team_id", default=None)
    tz: Optional[str] = Field(alias="tz", default=None)
    tz_label: Optional[str] = Field(alias="tz_label", default=None)
    tz_offset: Optional[int] = Field(alias="tz_offset", default=None)
    updated: Optional[int] = Field(alias="updated", default=None)
    who_can_share_contact_card: Optional[str] = Field(
        alias="who_can_share_contact_card", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetUserByEmailResponse"], src_dict: Dict[str, Any]):
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

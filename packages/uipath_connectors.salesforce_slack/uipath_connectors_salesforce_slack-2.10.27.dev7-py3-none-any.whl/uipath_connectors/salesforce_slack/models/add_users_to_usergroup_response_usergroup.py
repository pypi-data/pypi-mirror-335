from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.add_users_to_usergroup_response_usergroup_prefs import (
    AddUsersToUsergroupResponseUsergroupPrefs,
)


class AddUsersToUsergroupResponseUsergroup(BaseModel):
    """
    Attributes:
        auto_provision (Optional[bool]):
        channel_count (Optional[int]):  Example: 0.0.
        created_by (Optional[str]):  Example: U02K95UU71Q.
        date_create (Optional[int]):  Example: 1.676803736E9.
        date_delete (Optional[int]):  Example: 0.0.
        date_update (Optional[int]):  Example: 1.683785723E9.
        description (Optional[str]):  Example: testing.
        enterprise_subteam_id (Optional[str]):
        handle (Optional[str]):  Example: update-test-team-29468.
        id (Optional[str]):  Example: S04Q3GYSMJS.
        is_external (Optional[bool]):
        is_subteam (Optional[bool]):  Example: True.
        is_usergroup (Optional[bool]):  Example: True.
        name (Optional[str]):  Example: Alpha Test Team 23840.
        prefs (Optional[AddUsersToUsergroupResponseUsergroupPrefs]):
        team_id (Optional[str]):  Example: T02KZCJHY1W.
        updated_by (Optional[str]):  Example: U02K95UU71Q.
        user_count (Optional[int]):  Example: 3.0.
        users (Optional[list[str]]):  Example: ['U02K95UU71Q', 'U04Q3GTCF7G', 'U04QA5052EN'].
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    auto_provision: Optional[bool] = Field(alias="auto_provision", default=None)
    channel_count: Optional[int] = Field(alias="channel_count", default=None)
    created_by: Optional[str] = Field(alias="created_by", default=None)
    date_create: Optional[int] = Field(alias="date_create", default=None)
    date_delete: Optional[int] = Field(alias="date_delete", default=None)
    date_update: Optional[int] = Field(alias="date_update", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    enterprise_subteam_id: Optional[str] = Field(
        alias="enterprise_subteam_id", default=None
    )
    handle: Optional[str] = Field(alias="handle", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    is_external: Optional[bool] = Field(alias="is_external", default=None)
    is_subteam: Optional[bool] = Field(alias="is_subteam", default=None)
    is_usergroup: Optional[bool] = Field(alias="is_usergroup", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    prefs: Optional["AddUsersToUsergroupResponseUsergroupPrefs"] = Field(
        alias="prefs", default=None
    )
    team_id: Optional[str] = Field(alias="team_id", default=None)
    updated_by: Optional[str] = Field(alias="updated_by", default=None)
    user_count: Optional[int] = Field(alias="user_count", default=None)
    users: Optional[list[str]] = Field(alias="users", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["AddUsersToUsergroupResponseUsergroup"], src_dict: Dict[str, Any]
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

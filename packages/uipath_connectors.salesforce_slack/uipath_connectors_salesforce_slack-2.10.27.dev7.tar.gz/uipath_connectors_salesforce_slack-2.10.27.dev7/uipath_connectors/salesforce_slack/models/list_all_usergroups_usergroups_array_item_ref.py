from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.list_all_usergroups_usergroups_prefs import (
    ListAllUsergroupsUsergroupsPrefs,
)


class ListAllUsergroupsUsergroupsArrayItemRef(BaseModel):
    """
    Attributes:
        auto_provision (Optional[bool]):
        channel_count (Optional[int]):
        created_by (Optional[str]):
        date_create (Optional[int]):
        date_delete (Optional[int]):
        date_update (Optional[int]):
        description (Optional[str]):
        enterprise_subteam_id (Optional[str]):
        handle (Optional[str]):
        id (Optional[str]):
        is_external (Optional[bool]):
        is_subteam (Optional[bool]):
        is_usergroup (Optional[bool]):
        name (Optional[str]):
        prefs (Optional[ListAllUsergroupsUsergroupsPrefs]):
        team_id (Optional[str]):
        user_count (Optional[int]):
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
    prefs: Optional["ListAllUsergroupsUsergroupsPrefs"] = Field(
        alias="prefs", default=None
    )
    team_id: Optional[str] = Field(alias="team_id", default=None)
    user_count: Optional[int] = Field(alias="user_count", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["ListAllUsergroupsUsergroupsArrayItemRef"], src_dict: Dict[str, Any]
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

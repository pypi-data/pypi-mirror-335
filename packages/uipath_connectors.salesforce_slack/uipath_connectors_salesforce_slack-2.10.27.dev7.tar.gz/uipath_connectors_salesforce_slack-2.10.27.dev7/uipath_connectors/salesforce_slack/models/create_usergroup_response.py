from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_usergroup_response_prefs import CreateUsergroupResponsePrefs


class CreateUsergroupResponse(BaseModel):
    """
    Attributes:
        auto_type (Optional[str]):
        created_by (Optional[str]):  Example: U060RNRCZ.
        date_create (Optional[int]):  Example: 1.446746793E9.
        date_delete (Optional[int]):  Example: 0.0.
        date_update (Optional[int]):  Example: 1.446746793E9.
        deleted_by (Optional[str]):
        description (Optional[str]): A short description of the user group Example: Marketing gurus, PR experts and
                product advocates..
        handle (Optional[str]): A mention handle that is unique among channels, users and user groups. For example,
                @test_usergroup Example: marketing-team.
        id (Optional[str]): The unique id of the conversauser group. Example: S0615G0KT.
        is_external (Optional[bool]):
        is_usergroup (Optional[bool]):  Example: True.
        name (Optional[str]): A name for the user group. Must be unique among user groups Example: Marketing Team.
        prefs (Optional[CreateUsergroupResponsePrefs]):
        team_id (Optional[str]):  Example: T060RNRCH.
        updated_by (Optional[str]):  Example: U060RNRCZ.
        user_count (Optional[int]):  Example: 0.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    auto_type: Optional[str] = Field(alias="auto_type", default=None)
    created_by: Optional[str] = Field(alias="created_by", default=None)
    date_create: Optional[int] = Field(alias="date_create", default=None)
    date_delete: Optional[int] = Field(alias="date_delete", default=None)
    date_update: Optional[int] = Field(alias="date_update", default=None)
    deleted_by: Optional[str] = Field(alias="deleted_by", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    handle: Optional[str] = Field(alias="handle", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    is_external: Optional[bool] = Field(alias="is_external", default=None)
    is_usergroup: Optional[bool] = Field(alias="is_usergroup", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    prefs: Optional["CreateUsergroupResponsePrefs"] = Field(alias="prefs", default=None)
    team_id: Optional[str] = Field(alias="team_id", default=None)
    updated_by: Optional[str] = Field(alias="updated_by", default=None)
    user_count: Optional[int] = Field(alias="user_count", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateUsergroupResponse"], src_dict: Dict[str, Any]):
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

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.add_users_to_usergroup_response_usergroup import (
    AddUsersToUsergroupResponseUsergroup,
)
from ..models.add_users_to_usergroup_response_response_metadata import (
    AddUsersToUsergroupResponseResponseMetadata,
)


class AddUsersToUsergroupResponse(BaseModel):
    """
    Attributes:
        ok (Optional[bool]):  Example: True.
        response_metadata (Optional[AddUsersToUsergroupResponseResponseMetadata]):
        usergroup (Optional[AddUsersToUsergroupResponseUsergroup]):
        warning (Optional[str]):  Example: missing_charset.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    ok: Optional[bool] = Field(alias="ok", default=None)
    response_metadata: Optional["AddUsersToUsergroupResponseResponseMetadata"] = Field(
        alias="response_metadata", default=None
    )
    usergroup: Optional["AddUsersToUsergroupResponseUsergroup"] = Field(
        alias="usergroup", default=None
    )
    warning: Optional[str] = Field(alias="warning", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["AddUsersToUsergroupResponse"], src_dict: Dict[str, Any]):
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

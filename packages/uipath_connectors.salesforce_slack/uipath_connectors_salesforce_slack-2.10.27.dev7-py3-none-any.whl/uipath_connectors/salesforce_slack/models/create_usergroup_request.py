from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class CreateUsergroupRequest(BaseModel):
    """
    Attributes:
        handle (str): A mention handle that is unique among channels, users and user groups. For example,
                @test_usergroup Example: marketing-team.
        name (str): A name for the user group. Must be unique among user groups Example: Marketing Team.
        channels (Optional[str]): Default Channel IDs Example: D02EBQBE7QS,D04RX3MJHMZ.
        description (Optional[str]): A short description of the user group Example: Marketing gurus, PR experts and
                product advocates..
        include_count (Optional[bool]):  Example: True.
        team_id (Optional[str]):  Example: T060RNRCH.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    handle: str = Field(alias="handle")
    name: str = Field(alias="name")
    channels: Optional[str] = Field(alias="channels", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    include_count: Optional[bool] = Field(alias="include_count", default=None)
    team_id: Optional[str] = Field(alias="team_id", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateUsergroupRequest"], src_dict: Dict[str, Any]):
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

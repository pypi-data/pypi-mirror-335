from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class CreateChannelResponsePurpose(BaseModel):
    """
    Attributes:
        creator (Optional[str]):  Example: UCTGFDTEV.
        last_set (Optional[int]):  Example: 1.536962679E9.
        value (Optional[str]):  Example: A place for non-work-related flimflam, faffing, hodge-podge or jibber-jabber
                you'd prefer to keep out of more focused work-related channels..
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    creator: Optional[str] = Field(alias="creator", default=None)
    last_set: Optional[int] = Field(alias="last_set", default=None)
    value: Optional[str] = Field(alias="value", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateChannelResponsePurpose"], src_dict: Dict[str, Any]):
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

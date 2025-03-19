from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class SetChannelTopicResponseLatest(BaseModel):
    """
    Attributes:
        subtype (Optional[str]):  Example: channel_topic.
        text (Optional[str]):  Example: set the channel topic: Apply topically for best effects.
        topic (Optional[str]):  Example: Apply topically for best effects.
        ts (Optional[str]):  Example: 1649952691.429799.
        type_ (Optional[str]):  Example: message.
        user (Optional[str]):  Example: U12345678.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    subtype: Optional[str] = Field(alias="subtype", default=None)
    text: Optional[str] = Field(alias="text", default=None)
    topic: Optional[str] = Field(alias="topic", default=None)
    ts: Optional[str] = Field(alias="ts", default=None)
    type_: Optional[str] = Field(alias="type", default=None)
    user: Optional[str] = Field(alias="user", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SetChannelTopicResponseLatest"], src_dict: Dict[str, Any]):
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

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Type


class SetChannelTopicRequest(BaseModel):
    """
    Attributes:
        channel (str): Channel ID Example: C1234567890.
        topic (str): The topic of the conversation. This is visible in the header of the channel Example: Apply
                topically for best effects.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    channel: str = Field(alias="channel")
    topic: str = Field(alias="topic")

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SetChannelTopicRequest"], src_dict: Dict[str, Any]):
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

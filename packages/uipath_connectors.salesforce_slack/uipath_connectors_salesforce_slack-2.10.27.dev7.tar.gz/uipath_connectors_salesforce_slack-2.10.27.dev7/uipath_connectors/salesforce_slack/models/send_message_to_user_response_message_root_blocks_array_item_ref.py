from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.send_message_to_user_response_message_root_blocks_elements_array_item_ref import (
    SendMessageToUserResponseMessageRootBlocksElementsArrayItemRef,
)


class SendMessageToUserResponseMessageRootBlocksArrayItemRef(BaseModel):
    """
    Attributes:
        block_id (Optional[str]):  Example: /5z1a.
        elements (Optional[list['SendMessageToUserResponseMessageRootBlocksElementsArrayItemRef']]):
        type_ (Optional[str]):  Example: rich_text.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    block_id: Optional[str] = Field(alias="block_id", default=None)
    elements: Optional[
        list["SendMessageToUserResponseMessageRootBlocksElementsArrayItemRef"]
    ] = Field(alias="elements", default=None)
    type_: Optional[str] = Field(alias="type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SendMessageToUserResponseMessageRootBlocksArrayItemRef"],
        src_dict: Dict[str, Any],
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

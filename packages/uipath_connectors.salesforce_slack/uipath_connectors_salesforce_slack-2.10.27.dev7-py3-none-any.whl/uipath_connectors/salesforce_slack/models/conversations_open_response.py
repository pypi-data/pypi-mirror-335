from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class ConversationsOpenResponse(BaseModel):
    """
    Attributes:
        created (Optional[int]):  Example: 1.460147748E9.
        id (Optional[str]):  Example: D069C7QFK.
        is_im (Optional[bool]):  Example: True.
        is_open (Optional[bool]):  Example: True.
        is_org_shared (Optional[bool]):
        last_read (Optional[str]):  Example: 0000000000.000000.
        latest (Optional[str]):
        priority (Optional[int]):  Example: 0.0.
        unread_count (Optional[int]):  Example: 0.0.
        unread_count_display (Optional[int]):  Example: 0.0.
        user (Optional[str]):  Example: U069C7QF3.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    created: Optional[int] = Field(alias="created", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    is_im: Optional[bool] = Field(alias="is_im", default=None)
    is_open: Optional[bool] = Field(alias="is_open", default=None)
    is_org_shared: Optional[bool] = Field(alias="is_org_shared", default=None)
    last_read: Optional[str] = Field(alias="last_read", default=None)
    latest: Optional[str] = Field(alias="latest", default=None)
    priority: Optional[int] = Field(alias="priority", default=None)
    unread_count: Optional[int] = Field(alias="unread_count", default=None)
    unread_count_display: Optional[int] = Field(
        alias="unread_count_display", default=None
    )
    user: Optional[str] = Field(alias="user", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ConversationsOpenResponse"], src_dict: Dict[str, Any]):
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

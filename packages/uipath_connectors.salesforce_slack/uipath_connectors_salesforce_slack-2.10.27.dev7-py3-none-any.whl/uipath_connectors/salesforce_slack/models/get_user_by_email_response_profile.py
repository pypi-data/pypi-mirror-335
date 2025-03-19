from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class GetUserByEmailResponseProfile(BaseModel):
    """
    Attributes:
        avatar_hash (Optional[str]):  Example: g6d998d80169.
        display_name (Optional[str]):
        display_name_normalized (Optional[str]):
        email (Optional[str]):  Example: dhandu1995@gmail.com.
        huddle_state (Optional[str]):  Example: default_unset.
        image_192 (Optional[str]):  Example:
                https://secure.gravatar.com/avatar/6d998d801691b9d9198fe83d3f77c9f7.jpg?s=192&d=https%3A%2F%2Fa.slack-
                edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0025-192.png.
        image_24 (Optional[str]):  Example:
                https://secure.gravatar.com/avatar/6d998d801691b9d9198fe83d3f77c9f7.jpg?s=24&d=https%3A%2F%2Fa.slack-
                edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0025-24.png.
        image_32 (Optional[str]):  Example:
                https://secure.gravatar.com/avatar/6d998d801691b9d9198fe83d3f77c9f7.jpg?s=32&d=https%3A%2F%2Fa.slack-
                edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0025-32.png.
        image_48 (Optional[str]):  Example:
                https://secure.gravatar.com/avatar/6d998d801691b9d9198fe83d3f77c9f7.jpg?s=48&d=https%3A%2F%2Fa.slack-
                edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0025-48.png.
        image_512 (Optional[str]):  Example:
                https://secure.gravatar.com/avatar/6d998d801691b9d9198fe83d3f77c9f7.jpg?s=512&d=https%3A%2F%2Fa.slack-
                edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0025-512.png.
        image_72 (Optional[str]):  Example:
                https://secure.gravatar.com/avatar/6d998d801691b9d9198fe83d3f77c9f7.jpg?s=72&d=https%3A%2F%2Fa.slack-
                edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0025-72.png.
        phone (Optional[str]):
        real_name (Optional[str]):  Example: dhandu1995.
        real_name_normalized (Optional[str]):  Example: dhandu1995.
        skype (Optional[str]):
        status_emoji (Optional[str]):
        status_expiration (Optional[int]):  Example: 0.0.
        status_text (Optional[str]):
        status_text_canonical (Optional[str]):
        team (Optional[str]):  Example: T01G1P7CKR8.
        title (Optional[str]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    avatar_hash: Optional[str] = Field(alias="avatar_hash", default=None)
    display_name: Optional[str] = Field(alias="display_name", default=None)
    display_name_normalized: Optional[str] = Field(
        alias="display_name_normalized", default=None
    )
    email: Optional[str] = Field(alias="email", default=None)
    huddle_state: Optional[str] = Field(alias="huddle_state", default=None)
    image_192: Optional[str] = Field(alias="image_192", default=None)
    image_24: Optional[str] = Field(alias="image_24", default=None)
    image_32: Optional[str] = Field(alias="image_32", default=None)
    image_48: Optional[str] = Field(alias="image_48", default=None)
    image_512: Optional[str] = Field(alias="image_512", default=None)
    image_72: Optional[str] = Field(alias="image_72", default=None)
    phone: Optional[str] = Field(alias="phone", default=None)
    real_name: Optional[str] = Field(alias="real_name", default=None)
    real_name_normalized: Optional[str] = Field(
        alias="real_name_normalized", default=None
    )
    skype: Optional[str] = Field(alias="skype", default=None)
    status_emoji: Optional[str] = Field(alias="status_emoji", default=None)
    status_expiration: Optional[int] = Field(alias="status_expiration", default=None)
    status_text: Optional[str] = Field(alias="status_text", default=None)
    status_text_canonical: Optional[str] = Field(
        alias="status_text_canonical", default=None
    )
    team: Optional[str] = Field(alias="team", default=None)
    title: Optional[str] = Field(alias="title", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetUserByEmailResponseProfile"], src_dict: Dict[str, Any]):
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

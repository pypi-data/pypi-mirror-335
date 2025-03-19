from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class ListAllUsersProfile(BaseModel):
    """
    Attributes:
        avatar_hash (Optional[str]):  Example: ge3b51ca72de.
        display_name (Optional[str]):  Example: spengler.
        display_name_normalized (Optional[str]):  Example: spengler.
        email (Optional[str]):  Example: spengler@ghostbusters.example.com.
        first_name (Optional[str]):  Example: Glinda.
        image_1024 (Optional[str]):  Example: https://a.slack-edge.com...png.
        image_192 (Optional[str]):  Example: https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg.
        image_24 (Optional[str]):  Example: https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg.
        image_32 (Optional[str]):  Example: https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg.
        image_48 (Optional[str]):  Example: https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg.
        image_512 (Optional[str]):  Example: https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg.
        image_72 (Optional[str]):  Example: https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg.
        image_original (Optional[str]):  Example: https://a.slack-edge.com...png.
        last_name (Optional[str]):  Example: Southgood.
        phone (Optional[str]):
        real_name (Optional[str]):  Example: Egon Spengler.
        real_name_normalized (Optional[str]):  Example: Egon Spengler.
        skype (Optional[str]):
        status_emoji (Optional[str]):  Example: :books:.
        status_text (Optional[str]):  Example: Print is dead.
        team (Optional[str]):  Example: T012AB3C4.
        title (Optional[str]):  Example: Glinda the Good.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    avatar_hash: Optional[str] = Field(alias="avatar_hash", default=None)
    display_name: Optional[str] = Field(alias="display_name", default=None)
    display_name_normalized: Optional[str] = Field(
        alias="display_name_normalized", default=None
    )
    email: Optional[str] = Field(alias="email", default=None)
    first_name: Optional[str] = Field(alias="first_name", default=None)
    image_1024: Optional[str] = Field(alias="image_1024", default=None)
    image_192: Optional[str] = Field(alias="image_192", default=None)
    image_24: Optional[str] = Field(alias="image_24", default=None)
    image_32: Optional[str] = Field(alias="image_32", default=None)
    image_48: Optional[str] = Field(alias="image_48", default=None)
    image_512: Optional[str] = Field(alias="image_512", default=None)
    image_72: Optional[str] = Field(alias="image_72", default=None)
    image_original: Optional[str] = Field(alias="image_original", default=None)
    last_name: Optional[str] = Field(alias="last_name", default=None)
    phone: Optional[str] = Field(alias="phone", default=None)
    real_name: Optional[str] = Field(alias="real_name", default=None)
    real_name_normalized: Optional[str] = Field(
        alias="real_name_normalized", default=None
    )
    skype: Optional[str] = Field(alias="skype", default=None)
    status_emoji: Optional[str] = Field(alias="status_emoji", default=None)
    status_text: Optional[str] = Field(alias="status_text", default=None)
    team: Optional[str] = Field(alias="team", default=None)
    title: Optional[str] = Field(alias="title", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ListAllUsersProfile"], src_dict: Dict[str, Any]):
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

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.upload_file_response_reactions_array_item_ref import (
    UploadFileResponseReactionsArrayItemRef,
)


class UploadFileResponse(BaseModel):
    """
    Attributes:
        channels (Optional[list[str]]):
        comments_count (Optional[int]):
        created (Optional[int]):
        date_delete (Optional[int]):
        display_as_bot (Optional[bool]):
        editable (Optional[bool]):
        editor (Optional[str]):
        external_id (Optional[str]):
        external_type (Optional[str]):
        external_url (Optional[str]):
        file_access (Optional[str]): The access permissions set for the file. Example: visible.
        filetype (Optional[str]):
        groups (Optional[list[str]]):
        has_more_shares (Optional[bool]): Indicates if there are more shares available.
        has_rich_preview (Optional[bool]):
        id (Optional[str]): The output ID of the file uploaded
        image_exif_rotation (Optional[int]):
        ims (Optional[list[str]]):
        is_external (Optional[bool]):
        is_public (Optional[bool]):
        is_starred (Optional[bool]):
        is_tombstoned (Optional[bool]):
        mimetype (Optional[str]):
        mode (Optional[str]):
        name (Optional[str]):
        non_owner_editable (Optional[bool]):
        num_stars (Optional[int]):
        original_h (Optional[int]):
        original_w (Optional[int]):
        permalink (Optional[str]):
        permalink_public (Optional[str]):
        pinned_to (Optional[list[str]]):
        pretty_type (Optional[str]):
        preview (Optional[str]):
        public_url_shared (Optional[bool]):
        reactions (Optional[list['UploadFileResponseReactionsArrayItemRef']]):
        size (Optional[int]):
        source_team (Optional[str]):
        state (Optional[str]):
        thumb_1024 (Optional[str]):
        thumb_1024_h (Optional[int]):
        thumb_1024_w (Optional[int]):
        thumb_160 (Optional[str]):
        thumb_360 (Optional[str]):
        thumb_360_h (Optional[int]):
        thumb_360_w (Optional[int]):
        thumb_480 (Optional[str]):
        thumb_480_h (Optional[int]):
        thumb_480_w (Optional[int]):
        thumb_64 (Optional[str]):
        thumb_720 (Optional[str]):
        thumb_720_h (Optional[int]):
        thumb_720_w (Optional[int]):
        thumb_80 (Optional[str]):
        thumb_800 (Optional[str]):
        thumb_800_h (Optional[int]):
        thumb_800_w (Optional[int]):
        thumb_960 (Optional[str]):
        thumb_960_h (Optional[int]):
        thumb_960_w (Optional[int]):
        thumb_tiny (Optional[str]):
        timestamp (Optional[int]):
        title (Optional[str]):
        updated (Optional[int]):
        url_private (Optional[str]): The output URL of the file uploaded
        url_private_download (Optional[str]):
        user (Optional[str]):
        user_team (Optional[str]): The unique identifier for the user's team. Example: T01G1P7CKR8.
        username (Optional[str]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    channels: Optional[list[str]] = Field(alias="channels", default=None)
    comments_count: Optional[int] = Field(alias="comments_count", default=None)
    created: Optional[int] = Field(alias="created", default=None)
    date_delete: Optional[int] = Field(alias="date_delete", default=None)
    display_as_bot: Optional[bool] = Field(alias="display_as_bot", default=None)
    editable: Optional[bool] = Field(alias="editable", default=None)
    editor: Optional[str] = Field(alias="editor", default=None)
    external_id: Optional[str] = Field(alias="external_id", default=None)
    external_type: Optional[str] = Field(alias="external_type", default=None)
    external_url: Optional[str] = Field(alias="external_url", default=None)
    file_access: Optional[str] = Field(alias="file_access", default=None)
    filetype: Optional[str] = Field(alias="filetype", default=None)
    groups: Optional[list[str]] = Field(alias="groups", default=None)
    has_more_shares: Optional[bool] = Field(alias="has_more_shares", default=None)
    has_rich_preview: Optional[bool] = Field(alias="has_rich_preview", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    image_exif_rotation: Optional[int] = Field(
        alias="image_exif_rotation", default=None
    )
    ims: Optional[list[str]] = Field(alias="ims", default=None)
    is_external: Optional[bool] = Field(alias="is_external", default=None)
    is_public: Optional[bool] = Field(alias="is_public", default=None)
    is_starred: Optional[bool] = Field(alias="is_starred", default=None)
    is_tombstoned: Optional[bool] = Field(alias="is_tombstoned", default=None)
    mimetype: Optional[str] = Field(alias="mimetype", default=None)
    mode: Optional[str] = Field(alias="mode", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    non_owner_editable: Optional[bool] = Field(alias="non_owner_editable", default=None)
    num_stars: Optional[int] = Field(alias="num_stars", default=None)
    original_h: Optional[int] = Field(alias="original_h", default=None)
    original_w: Optional[int] = Field(alias="original_w", default=None)
    permalink: Optional[str] = Field(alias="permalink", default=None)
    permalink_public: Optional[str] = Field(alias="permalink_public", default=None)
    pinned_to: Optional[list[str]] = Field(alias="pinned_to", default=None)
    pretty_type: Optional[str] = Field(alias="pretty_type", default=None)
    preview: Optional[str] = Field(alias="preview", default=None)
    public_url_shared: Optional[bool] = Field(alias="public_url_shared", default=None)
    reactions: Optional[list["UploadFileResponseReactionsArrayItemRef"]] = Field(
        alias="reactions", default=None
    )
    size: Optional[int] = Field(alias="size", default=None)
    source_team: Optional[str] = Field(alias="source_team", default=None)
    state: Optional[str] = Field(alias="state", default=None)
    thumb_1024: Optional[str] = Field(alias="thumb_1024", default=None)
    thumb_1024_h: Optional[int] = Field(alias="thumb_1024_h", default=None)
    thumb_1024_w: Optional[int] = Field(alias="thumb_1024_w", default=None)
    thumb_160: Optional[str] = Field(alias="thumb_160", default=None)
    thumb_360: Optional[str] = Field(alias="thumb_360", default=None)
    thumb_360_h: Optional[int] = Field(alias="thumb_360_h", default=None)
    thumb_360_w: Optional[int] = Field(alias="thumb_360_w", default=None)
    thumb_480: Optional[str] = Field(alias="thumb_480", default=None)
    thumb_480_h: Optional[int] = Field(alias="thumb_480_h", default=None)
    thumb_480_w: Optional[int] = Field(alias="thumb_480_w", default=None)
    thumb_64: Optional[str] = Field(alias="thumb_64", default=None)
    thumb_720: Optional[str] = Field(alias="thumb_720", default=None)
    thumb_720_h: Optional[int] = Field(alias="thumb_720_h", default=None)
    thumb_720_w: Optional[int] = Field(alias="thumb_720_w", default=None)
    thumb_80: Optional[str] = Field(alias="thumb_80", default=None)
    thumb_800: Optional[str] = Field(alias="thumb_800", default=None)
    thumb_800_h: Optional[int] = Field(alias="thumb_800_h", default=None)
    thumb_800_w: Optional[int] = Field(alias="thumb_800_w", default=None)
    thumb_960: Optional[str] = Field(alias="thumb_960", default=None)
    thumb_960_h: Optional[int] = Field(alias="thumb_960_h", default=None)
    thumb_960_w: Optional[int] = Field(alias="thumb_960_w", default=None)
    thumb_tiny: Optional[str] = Field(alias="thumb_tiny", default=None)
    timestamp: Optional[int] = Field(alias="timestamp", default=None)
    title: Optional[str] = Field(alias="title", default=None)
    updated: Optional[int] = Field(alias="updated", default=None)
    url_private: Optional[str] = Field(alias="url_private", default=None)
    url_private_download: Optional[str] = Field(
        alias="url_private_download", default=None
    )
    user: Optional[str] = Field(alias="user", default=None)
    user_team: Optional[str] = Field(alias="user_team", default=None)
    username: Optional[str] = Field(alias="username", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["UploadFileResponse"], src_dict: Dict[str, Any]):
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

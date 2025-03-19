from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class GetAttachmentResponse(BaseModel):
    """
    Attributes:
        average_image_color (Optional[str]): Average image color
        chunk_size_bytes (Optional[int]): Chunk size bytes
        compressed (Optional[str]): Compressed
        content_type (Optional[str]): Content type
        download_link (Optional[str]): Download link
        file_name (Optional[str]): File name
        hash_ (Optional[str]): Hash
        image_height (Optional[int]): Image height
        image_width (Optional[int]): Image width
        size_bytes (Optional[int]): Size bytes
        size_compressed (Optional[int]): Size compressed
        state (Optional[str]): State
        sys_created_by (Optional[str]): Created by
        sys_created_on (Optional[datetime.datetime]): Created
        sys_id (Optional[str]): Sys ID
        sys_mod_count (Optional[int]): Updates
        sys_updated_by (Optional[str]): Updated by
        sys_updated_on (Optional[datetime.datetime]): Updated
        table_name (Optional[str]): Table name
        table_sys_id (Optional[str]): Table sys ID
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    average_image_color: Optional[str] = Field(
        alias="average_image_color", default=None
    )
    chunk_size_bytes: Optional[int] = Field(alias="chunk_size_bytes", default=None)
    compressed: Optional[str] = Field(alias="compressed", default=None)
    content_type: Optional[str] = Field(alias="content_type", default=None)
    download_link: Optional[str] = Field(alias="download_link", default=None)
    file_name: Optional[str] = Field(alias="file_name", default=None)
    hash_: Optional[str] = Field(alias="hash", default=None)
    image_height: Optional[int] = Field(alias="image_height", default=None)
    image_width: Optional[int] = Field(alias="image_width", default=None)
    size_bytes: Optional[int] = Field(alias="size_bytes", default=None)
    size_compressed: Optional[int] = Field(alias="size_compressed", default=None)
    state: Optional[str] = Field(alias="state", default=None)
    sys_created_by: Optional[str] = Field(alias="sys_created_by", default=None)
    sys_created_on: Optional[datetime.datetime] = Field(
        alias="sys_created_on", default=None
    )
    sys_id: Optional[str] = Field(alias="sys_id", default=None)
    sys_mod_count: Optional[int] = Field(alias="sys_mod_count", default=None)
    sys_updated_by: Optional[str] = Field(alias="sys_updated_by", default=None)
    sys_updated_on: Optional[datetime.datetime] = Field(
        alias="sys_updated_on", default=None
    )
    table_name: Optional[str] = Field(alias="table_name", default=None)
    table_sys_id: Optional[str] = Field(alias="table_sys_id", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetAttachmentResponse"], src_dict: Dict[str, Any]):
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

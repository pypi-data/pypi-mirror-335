from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class AddAttachmentResponse(BaseModel):
    """
    Attributes:
        average_image_color (Optional[str]):
        chunk_size_bytes (Optional[str]):  Example: 700000.
        compressed (Optional[str]):  Example: true.
        content_type (Optional[str]):  Example: */*.
        download_link (Optional[str]):  Example: https://dev111679.service-
                now.com/api/now/attachment/012801614700ed10d282767a436d4367/file.
        file_name (Optional[str]):  Example: Ac5.
        hash_ (Optional[str]):  Example: 6df6316b4db0843b4fe18f755e4ab593a0eee4effd547c9be0ca8e0158e6e1b8.
        image_height (Optional[str]):
        image_width (Optional[str]):
        size_bytes (Optional[str]):  Example: 66764.
        size_compressed (Optional[str]):  Example: 6095.
        state (Optional[str]):  Example: pending.
        sys_created_by (Optional[str]):  Example: admin.
        sys_created_on (Optional[datetime.datetime]):  Example: 2022-12-28 09:11:27.
        sys_id (Optional[str]): The ID of the attachment. Example: 012801614700ed10d282767a436d4367.
        sys_mod_count (Optional[str]):  Example: 0.
        sys_tags (Optional[str]):
        sys_updated_by (Optional[str]):  Example: admin.
        sys_updated_on (Optional[datetime.datetime]):  Example: 2022-12-28 09:11:27.
        table_name (Optional[str]):  Example: sys_product_help.
        table_sys_id (Optional[str]):  Example: 750129c94f12020031577d2ca310c7a4.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    average_image_color: Optional[str] = Field(
        alias="average_image_color", default=None
    )
    chunk_size_bytes: Optional[str] = Field(alias="chunk_size_bytes", default=None)
    compressed: Optional[str] = Field(alias="compressed", default=None)
    content_type: Optional[str] = Field(alias="content_type", default=None)
    download_link: Optional[str] = Field(alias="download_link", default=None)
    file_name: Optional[str] = Field(alias="file_name", default=None)
    hash_: Optional[str] = Field(alias="hash", default=None)
    image_height: Optional[str] = Field(alias="image_height", default=None)
    image_width: Optional[str] = Field(alias="image_width", default=None)
    size_bytes: Optional[str] = Field(alias="size_bytes", default=None)
    size_compressed: Optional[str] = Field(alias="size_compressed", default=None)
    state: Optional[str] = Field(alias="state", default=None)
    sys_created_by: Optional[str] = Field(alias="sys_created_by", default=None)
    sys_created_on: Optional[datetime.datetime] = Field(
        alias="sys_created_on", default=None
    )
    sys_id: Optional[str] = Field(alias="sys_id", default=None)
    sys_mod_count: Optional[str] = Field(alias="sys_mod_count", default=None)
    sys_tags: Optional[str] = Field(alias="sys_tags", default=None)
    sys_updated_by: Optional[str] = Field(alias="sys_updated_by", default=None)
    sys_updated_on: Optional[datetime.datetime] = Field(
        alias="sys_updated_on", default=None
    )
    table_name: Optional[str] = Field(alias="table_name", default=None)
    table_sys_id: Optional[str] = Field(alias="table_sys_id", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["AddAttachmentResponse"], src_dict: Dict[str, Any]):
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

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class UpdateIncidentTaskResponse(BaseModel):
    """
    Attributes:
        assigned_to (Optional[str]): Person primarily responsible for working this task Example:
                {value=02826bf03710200044e0bfc8b.
        assignment_group (Optional[str]): Group primarily responsible for working this task, if left blank the task will
                be automatically assigned. Example: {value=0a52d3dcd7011200f2d224837.
        description (Optional[str]): Detailed explanation of the task. Example: description.
        incident (Optional[str]): To begin, enter either the full or partial incident number (INC). Example:
                {value=1c741bd70b2322007518478d8.
        number (Optional[str]):  Example: TASK0021647.
        priority (Optional[int]): Sequence in which an incident or problem needs to be resolved, based on impact and
                urgency Example: 4.
        short_description (Optional[str]): Describes the impacted behavior of this task Example: testing.
        state (Optional[int]): Status of the task Example: 1.
        sys_created_on (Optional[datetime.datetime]):  Example: 2022-12-02 12:59:55.
        sys_id (Optional[str]): The ID of the incident task. Example: 1613c45d4763151064c42646926d43e1.
        sys_updated_on (Optional[datetime.datetime]):  Example: 2022-12-26 12:38:08.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    assigned_to: Optional[str] = Field(alias="assigned_to", default=None)
    assignment_group: Optional[str] = Field(alias="assignment_group", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    incident: Optional[str] = Field(alias="incident", default=None)
    number: Optional[str] = Field(alias="number", default=None)
    priority: Optional[int] = Field(alias="priority", default=None)
    short_description: Optional[str] = Field(alias="short_description", default=None)
    state: Optional[int] = Field(alias="state", default=None)
    sys_created_on: Optional[datetime.datetime] = Field(
        alias="sys_created_on", default=None
    )
    sys_id: Optional[str] = Field(alias="sys_id", default=None)
    sys_updated_on: Optional[datetime.datetime] = Field(
        alias="sys_updated_on", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["UpdateIncidentTaskResponse"], src_dict: Dict[str, Any]):
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

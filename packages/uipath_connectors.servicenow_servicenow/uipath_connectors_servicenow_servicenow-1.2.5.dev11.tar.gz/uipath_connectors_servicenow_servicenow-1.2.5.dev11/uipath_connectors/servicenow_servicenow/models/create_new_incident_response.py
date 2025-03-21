from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class CreateNewIncidentResponse(BaseModel):
    """
    Attributes:
        assigned_to (Optional[str]): Person primarily responsible for working this task Example:
                {value=02826bf03710200044e0bfc8b.
        caller_id (Optional[str]): Person who reported or is affected by this incident Example:
                005d500b536073005e0addeeff7b12f4.
        caller_id_link (Optional[str]):
        close_code (Optional[str]): Resolution code to be used in reporting
        close_notes (Optional[str]): Resolution notes for the incident
        closed_at (Optional[datetime.datetime]): Resolution date/time of the incident
        description (Optional[str]): Describes the impacted behavior of this incident Example: what is it?.
        impact (Optional[int]): The extent to which resolution of an incident can bear delay Example: 1.
        number (Optional[str]): The number of incident. Example: INC000456.
        opened_at (Optional[datetime.datetime]):  Example: 2022-2-8 00:44:53.
        short_description (Optional[str]): Describes the impacted behavior of this incident Example: what is it?.
        state (Optional[int]): Status of the incident
        sys_id (Optional[str]): The ID of incident. Example: 005d500b536073005e0addeeff7b12f4.
        urgency (Optional[int]): The extent to which resolution of an incident can bear delay Example: 1.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    assigned_to: Optional[str] = Field(alias="assigned_to", default=None)
    caller_id: Optional[str] = Field(alias="caller_id", default=None)
    caller_id_link: Optional[str] = Field(alias="caller_id_link", default=None)
    close_code: Optional[str] = Field(alias="close_code", default=None)
    close_notes: Optional[str] = Field(alias="close_notes", default=None)
    closed_at: Optional[datetime.datetime] = Field(alias="closed_at", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    impact: Optional[int] = Field(alias="impact", default=None)
    number: Optional[str] = Field(alias="number", default=None)
    opened_at: Optional[datetime.datetime] = Field(alias="opened_at", default=None)
    short_description: Optional[str] = Field(alias="short_description", default=None)
    state: Optional[int] = Field(alias="state", default=None)
    sys_id: Optional[str] = Field(alias="sys_id", default=None)
    urgency: Optional[int] = Field(alias="urgency", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateNewIncidentResponse"], src_dict: Dict[str, Any]):
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

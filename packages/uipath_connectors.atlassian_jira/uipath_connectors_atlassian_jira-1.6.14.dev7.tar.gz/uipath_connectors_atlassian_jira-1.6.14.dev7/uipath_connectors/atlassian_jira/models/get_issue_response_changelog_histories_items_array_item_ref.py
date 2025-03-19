from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class GetIssueResponseChangelogHistoriesItemsArrayItemRef(BaseModel):
    """
    Attributes:
        field (Optional[str]): The name of the field changed
        field_id (Optional[str]): The ID of the field changed
        fieldtype (Optional[str]): The type of the field changed
        from_ (Optional[str]): The details of the original value
        from_string (Optional[str]): The details of the original value as a string
        to (Optional[str]): The details of the new value
        to_string (Optional[str]): The details of the new value as a string
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    field: Optional[str] = Field(alias="field", default=None)
    field_id: Optional[str] = Field(alias="fieldId", default=None)
    fieldtype: Optional[str] = Field(alias="fieldtype", default=None)
    from_: Optional[str] = Field(alias="from", default=None)
    from_string: Optional[str] = Field(alias="fromString", default=None)
    to: Optional[str] = Field(alias="to", default=None)
    to_string: Optional[str] = Field(alias="toString", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetIssueResponseChangelogHistoriesItemsArrayItemRef"],
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

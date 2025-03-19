from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class GetIssueResponseTransitionFieldsSchema(BaseModel):
    """
    Attributes:
        custom (Optional[str]): If the field is a custom field, the URI of the field
        custom_id (Optional[int]): If the field is a custom field, the custom ID of the field
        items (Optional[str]): When the data type is an array, the name of the field items within the array
        system (Optional[str]): If the field is a system field, the name of the field
        type_ (Optional[str]): The data type of the field
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    custom: Optional[str] = Field(alias="custom", default=None)
    custom_id: Optional[int] = Field(alias="customId", default=None)
    items: Optional[str] = Field(alias="items", default=None)
    system: Optional[str] = Field(alias="system", default=None)
    type_: Optional[str] = Field(alias="type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetIssueResponseTransitionFieldsSchema"], src_dict: Dict[str, Any]
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

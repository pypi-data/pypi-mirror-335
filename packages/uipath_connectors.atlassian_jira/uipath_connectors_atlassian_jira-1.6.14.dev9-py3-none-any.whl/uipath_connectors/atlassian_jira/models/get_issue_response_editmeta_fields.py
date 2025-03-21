from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_issue_response_editmeta_fields_schema import (
    GetIssueResponseEditmetaFieldsSchema,
)


class GetIssueResponseEditmetaFields(BaseModel):
    """
    Attributes:
        allowed_values (Optional[list[str]]):
        auto_complete_url (Optional[str]): The URL that can be used to automatically complete the field
        default_value (Optional[str]): The default value of the field
        has_default_value (Optional[bool]): Whether the field has a default value
        key (Optional[str]): The key of the field
        name (Optional[str]): The name of the field
        operations (Optional[list[str]]):
        required (Optional[bool]): Whether the field is required
        schema (Optional[GetIssueResponseEditmetaFieldsSchema]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    allowed_values: Optional[list[str]] = Field(alias="allowedValues", default=None)
    auto_complete_url: Optional[str] = Field(alias="autoCompleteUrl", default=None)
    default_value: Optional[str] = Field(alias="defaultValue", default=None)
    has_default_value: Optional[bool] = Field(alias="hasDefaultValue", default=None)
    key: Optional[str] = Field(alias="key", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    operations: Optional[list[str]] = Field(alias="operations", default=None)
    required: Optional[bool] = Field(alias="required", default=None)
    schema: Optional["GetIssueResponseEditmetaFieldsSchema"] = Field(
        alias="schema", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetIssueResponseEditmetaFields"], src_dict: Dict[str, Any]
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

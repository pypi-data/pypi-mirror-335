from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_issue_response_changelog import GetIssueResponseChangelog
from ..models.get_issue_response_editmeta import GetIssueResponseEditmeta
from ..models.get_issue_response_fields import GetIssueResponseFields
from ..models.get_issue_response_fields_to_include import (
    GetIssueResponseFieldsToInclude,
)
from ..models.get_issue_response_history_metadata import GetIssueResponseHistoryMetadata
from ..models.get_issue_response_operations import GetIssueResponseOperations
from ..models.get_issue_response_properties_array_item_ref import (
    GetIssueResponsePropertiesArrayItemRef,
)
from ..models.get_issue_response_schema import GetIssueResponseSchema
from ..models.get_issue_response_transition import GetIssueResponseTransition
from ..models.get_issue_response_transitions_array_item_ref import (
    GetIssueResponseTransitionsArrayItemRef,
)
from ..models.get_issue_response_update import GetIssueResponseUpdate


class GetIssueResponse(BaseModel):
    """
    Attributes:
        changelog (Optional[GetIssueResponseChangelog]):
        editmeta (Optional[GetIssueResponseEditmeta]):
        expand (Optional[str]): Expand options that include additional issue details in the response
        fields (Optional[GetIssueResponseFields]):
        fields_to_include (Optional[GetIssueResponseFieldsToInclude]):
        history_metadata (Optional[GetIssueResponseHistoryMetadata]):
        id (Optional[str]): The ID of the issue
        key (Optional[str]): The key of the issue
        operations (Optional[GetIssueResponseOperations]):
        properties (Optional[list['GetIssueResponsePropertiesArrayItemRef']]):
        schema (Optional[GetIssueResponseSchema]):
        self_ (Optional[str]): The URL of the issue details
        transition (Optional[GetIssueResponseTransition]):
        transitions (Optional[list['GetIssueResponseTransitionsArrayItemRef']]):
        update (Optional[GetIssueResponseUpdate]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    changelog: Optional["GetIssueResponseChangelog"] = Field(
        alias="changelog", default=None
    )
    editmeta: Optional["GetIssueResponseEditmeta"] = Field(
        alias="editmeta", default=None
    )
    expand: Optional[str] = Field(alias="expand", default=None)
    fields: Optional["GetIssueResponseFields"] = Field(alias="fields", default=None)
    fields_to_include: Optional["GetIssueResponseFieldsToInclude"] = Field(
        alias="fieldsToInclude", default=None
    )
    history_metadata: Optional["GetIssueResponseHistoryMetadata"] = Field(
        alias="historyMetadata", default=None
    )
    id: Optional[str] = Field(alias="id", default=None)
    key: Optional[str] = Field(alias="key", default=None)
    operations: Optional["GetIssueResponseOperations"] = Field(
        alias="operations", default=None
    )
    properties: Optional[list["GetIssueResponsePropertiesArrayItemRef"]] = Field(
        alias="properties", default=None
    )
    schema: Optional["GetIssueResponseSchema"] = Field(alias="schema", default=None)
    self_: Optional[str] = Field(alias="self", default=None)
    transition: Optional["GetIssueResponseTransition"] = Field(
        alias="transition", default=None
    )
    transitions: Optional[list["GetIssueResponseTransitionsArrayItemRef"]] = Field(
        alias="transitions", default=None
    )
    update: Optional["GetIssueResponseUpdate"] = Field(alias="update", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetIssueResponse"], src_dict: Dict[str, Any]):
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

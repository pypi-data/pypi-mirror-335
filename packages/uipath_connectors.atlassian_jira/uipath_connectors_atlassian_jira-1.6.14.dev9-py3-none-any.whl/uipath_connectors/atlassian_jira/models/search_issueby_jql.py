from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_issueby_jql_changelog import SearchIssuebyJQLChangelog
from ..models.search_issueby_jql_editmeta import SearchIssuebyJQLEditmeta
from ..models.search_issueby_jql_fields import SearchIssuebyJQLFields
from ..models.search_issueby_jql_fields_to_include import (
    SearchIssuebyJQLFieldsToInclude,
)
from ..models.search_issueby_jql_operations import SearchIssuebyJQLOperations
from ..models.search_issueby_jql_schema import SearchIssuebyJQLSchema
from ..models.search_issueby_jql_transitions_array_item_ref import (
    SearchIssuebyJQLTransitionsArrayItemRef,
)


class SearchIssuebyJQL(BaseModel):
    """
    Attributes:
        changelog (Optional[SearchIssuebyJQLChangelog]):
        editmeta (Optional[SearchIssuebyJQLEditmeta]):
        expand (Optional[str]): Expand options that include additional issue details in the response.
        fields (Optional[SearchIssuebyJQLFields]):
        fields_to_include (Optional[SearchIssuebyJQLFieldsToInclude]):
        id (Optional[str]): The ID of the issue.
        key (Optional[str]): The key of the issue.
        operations (Optional[SearchIssuebyJQLOperations]):
        schema (Optional[SearchIssuebyJQLSchema]):
        self_ (Optional[str]): The URL of the issue details.
        transitions (Optional[list['SearchIssuebyJQLTransitionsArrayItemRef']]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    changelog: Optional["SearchIssuebyJQLChangelog"] = Field(
        alias="changelog", default=None
    )
    editmeta: Optional["SearchIssuebyJQLEditmeta"] = Field(
        alias="editmeta", default=None
    )
    expand: Optional[str] = Field(alias="expand", default=None)
    fields: Optional["SearchIssuebyJQLFields"] = Field(alias="fields", default=None)
    fields_to_include: Optional["SearchIssuebyJQLFieldsToInclude"] = Field(
        alias="fieldsToInclude", default=None
    )
    id: Optional[str] = Field(alias="id", default=None)
    key: Optional[str] = Field(alias="key", default=None)
    operations: Optional["SearchIssuebyJQLOperations"] = Field(
        alias="operations", default=None
    )
    schema: Optional["SearchIssuebyJQLSchema"] = Field(alias="schema", default=None)
    self_: Optional[str] = Field(alias="self", default=None)
    transitions: Optional[list["SearchIssuebyJQLTransitionsArrayItemRef"]] = Field(
        alias="transitions", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchIssuebyJQL"], src_dict: Dict[str, Any]):
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

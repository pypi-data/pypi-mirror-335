from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_issueby_jql_operations_link_groups_groups_array_item_ref import (
    SearchIssuebyJQLOperationsLinkGroupsGroupsArrayItemRef,
)
from ..models.search_issueby_jql_operations_link_groups_header import (
    SearchIssuebyJQLOperationsLinkGroupsHeader,
)
from ..models.search_issueby_jql_operations_link_groups_links_array_item_ref import (
    SearchIssuebyJQLOperationsLinkGroupsLinksArrayItemRef,
)


class SearchIssuebyJQLOperationsLinkGroupsArrayItemRef(BaseModel):
    """
    Attributes:
        groups (Optional[list['SearchIssuebyJQLOperationsLinkGroupsGroupsArrayItemRef']]):
        header (Optional[SearchIssuebyJQLOperationsLinkGroupsHeader]):
        id (Optional[str]):
        links (Optional[list['SearchIssuebyJQLOperationsLinkGroupsLinksArrayItemRef']]):
        style_class (Optional[str]):
        weight (Optional[int]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    groups: Optional[list["SearchIssuebyJQLOperationsLinkGroupsGroupsArrayItemRef"]] = (
        Field(alias="groups", default=None)
    )
    header: Optional["SearchIssuebyJQLOperationsLinkGroupsHeader"] = Field(
        alias="header", default=None
    )
    id: Optional[str] = Field(alias="id", default=None)
    links: Optional[list["SearchIssuebyJQLOperationsLinkGroupsLinksArrayItemRef"]] = (
        Field(alias="links", default=None)
    )
    style_class: Optional[str] = Field(alias="styleClass", default=None)
    weight: Optional[int] = Field(alias="weight", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchIssuebyJQLOperationsLinkGroupsArrayItemRef"],
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

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime
from ..models.get_issue_response_changelog_histories_author import (
    GetIssueResponseChangelogHistoriesAuthor,
)
from ..models.get_issue_response_changelog_histories_history_metadata import (
    GetIssueResponseChangelogHistoriesHistoryMetadata,
)
from ..models.get_issue_response_changelog_histories_items_array_item_ref import (
    GetIssueResponseChangelogHistoriesItemsArrayItemRef,
)


class GetIssueResponseChangelogHistoriesArrayItemRef(BaseModel):
    """
    Attributes:
        author (Optional[GetIssueResponseChangelogHistoriesAuthor]):
        created (Optional[datetime.datetime]): The date on which the change took place
        history_metadata (Optional[GetIssueResponseChangelogHistoriesHistoryMetadata]):
        id (Optional[str]): The ID of the changelog.
        items (Optional[list['GetIssueResponseChangelogHistoriesItemsArrayItemRef']]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    author: Optional["GetIssueResponseChangelogHistoriesAuthor"] = Field(
        alias="author", default=None
    )
    created: Optional[datetime.datetime] = Field(alias="created", default=None)
    history_metadata: Optional["GetIssueResponseChangelogHistoriesHistoryMetadata"] = (
        Field(alias="historyMetadata", default=None)
    )
    id: Optional[str] = Field(alias="id", default=None)
    items: Optional[list["GetIssueResponseChangelogHistoriesItemsArrayItemRef"]] = (
        Field(alias="items", default=None)
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetIssueResponseChangelogHistoriesArrayItemRef"],
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

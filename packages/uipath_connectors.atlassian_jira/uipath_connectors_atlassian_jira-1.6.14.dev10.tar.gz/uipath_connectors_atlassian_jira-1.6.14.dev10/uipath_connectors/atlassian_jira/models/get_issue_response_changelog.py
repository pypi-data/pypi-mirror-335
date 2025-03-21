from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_issue_response_changelog_histories_array_item_ref import (
    GetIssueResponseChangelogHistoriesArrayItemRef,
)


class GetIssueResponseChangelog(BaseModel):
    """
    Attributes:
        histories (Optional[list['GetIssueResponseChangelogHistoriesArrayItemRef']]):
        max_results (Optional[int]): The maximum number of results that could be on the page
        start_at (Optional[int]): The index of the first item returned on the page
        total (Optional[int]): The number of results on the page
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    histories: Optional[list["GetIssueResponseChangelogHistoriesArrayItemRef"]] = Field(
        alias="histories", default=None
    )
    max_results: Optional[int] = Field(alias="maxResults", default=None)
    start_at: Optional[int] = Field(alias="startAt", default=None)
    total: Optional[int] = Field(alias="total", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetIssueResponseChangelog"], src_dict: Dict[str, Any]):
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

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_issue_response_fields_issuelinks_inward_issue import (
    GetIssueResponseFieldsIssuelinksInwardIssue,
)
from ..models.get_issue_response_fields_issuelinks_outward_issue import (
    GetIssueResponseFieldsIssuelinksOutwardIssue,
)
from ..models.get_issue_response_fields_issuelinks_type import (
    GetIssueResponseFieldsIssuelinksType,
)


class GetIssueResponseFieldsIssuelinksArrayItemRef(BaseModel):
    """
    Attributes:
        id (Optional[str]): The unique identifier for the issue link Example: 10001.
        inward_issue (Optional[GetIssueResponseFieldsIssuelinksInwardIssue]):
        outward_issue (Optional[GetIssueResponseFieldsIssuelinksOutwardIssue]):
        type_ (Optional[GetIssueResponseFieldsIssuelinksType]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: Optional[str] = Field(alias="id", default=None)
    inward_issue: Optional["GetIssueResponseFieldsIssuelinksInwardIssue"] = Field(
        alias="inwardIssue", default=None
    )
    outward_issue: Optional["GetIssueResponseFieldsIssuelinksOutwardIssue"] = Field(
        alias="outwardIssue", default=None
    )
    type_: Optional["GetIssueResponseFieldsIssuelinksType"] = Field(
        alias="type", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetIssueResponseFieldsIssuelinksArrayItemRef"],
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

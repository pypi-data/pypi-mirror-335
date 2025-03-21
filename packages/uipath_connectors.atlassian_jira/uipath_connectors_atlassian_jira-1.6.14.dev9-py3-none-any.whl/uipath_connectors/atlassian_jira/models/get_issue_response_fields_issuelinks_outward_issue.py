from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_issue_response_fields_issuelinks_outward_issue_fields import (
    GetIssueResponseFieldsIssuelinksOutwardIssueFields,
)


class GetIssueResponseFieldsIssuelinksOutwardIssue(BaseModel):
    """
    Attributes:
        fields (Optional[GetIssueResponseFieldsIssuelinksOutwardIssueFields]):
        id (Optional[str]): The unique identifier for the linked outward issue Example: 10004L.
        key (Optional[str]): The key identifier for the outwardly linked issue Example: PR-2.
        self_ (Optional[str]): API endpoint URL for the linked outward issue Example: https://your-
                domain.atlassian.net/rest/api/3/issue/PR-2.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    fields: Optional["GetIssueResponseFieldsIssuelinksOutwardIssueFields"] = Field(
        alias="fields", default=None
    )
    id: Optional[str] = Field(alias="id", default=None)
    key: Optional[str] = Field(alias="key", default=None)
    self_: Optional[str] = Field(alias="self", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetIssueResponseFieldsIssuelinksOutwardIssue"],
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

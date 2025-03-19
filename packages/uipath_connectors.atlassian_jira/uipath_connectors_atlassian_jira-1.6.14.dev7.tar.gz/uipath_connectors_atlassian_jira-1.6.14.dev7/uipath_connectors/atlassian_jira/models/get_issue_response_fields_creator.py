from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_issue_response_fields_creator_avatar_urls import (
    GetIssueResponseFieldsCreatorAvatarUrls,
)


class GetIssueResponseFieldsCreator(BaseModel):
    """
    Attributes:
        account_id (Optional[str]):
        account_type (Optional[str]):
        active (Optional[bool]):
        avatar_urls (Optional[GetIssueResponseFieldsCreatorAvatarUrls]):
        display_name (Optional[str]):
        email_address (Optional[str]):
        self_ (Optional[str]):
        time_zone (Optional[str]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    account_id: Optional[str] = Field(alias="accountId", default=None)
    account_type: Optional[str] = Field(alias="accountType", default=None)
    active: Optional[bool] = Field(alias="active", default=None)
    avatar_urls: Optional["GetIssueResponseFieldsCreatorAvatarUrls"] = Field(
        alias="avatarUrls", default=None
    )
    display_name: Optional[str] = Field(alias="displayName", default=None)
    email_address: Optional[str] = Field(alias="emailAddress", default=None)
    self_: Optional[str] = Field(alias="self", default=None)
    time_zone: Optional[str] = Field(alias="timeZone", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetIssueResponseFieldsCreator"], src_dict: Dict[str, Any]):
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

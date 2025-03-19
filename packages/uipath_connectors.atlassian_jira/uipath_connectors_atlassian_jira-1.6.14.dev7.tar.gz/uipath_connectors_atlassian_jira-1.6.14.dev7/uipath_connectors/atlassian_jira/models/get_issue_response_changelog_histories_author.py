from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_issue_response_changelog_histories_author_avatar_urls import (
    GetIssueResponseChangelogHistoriesAuthorAvatarUrls,
)


class GetIssueResponseChangelogHistoriesAuthor(BaseModel):
    """
    Attributes:
        account_id (Optional[str]): The account ID of the user, which uniquely identifies the user across all Atlassian
                products. For example, *5b10ac8d82e05b22cc7d4ef5*.
        account_type (Optional[str]): The type of account represented by this user. This will be one of 'atlassian'
                (normal users), 'app' (application user) or 'customer' (Jira Service Desk customer user)
        active (Optional[bool]): Whether the user is active
        avatar_urls (Optional[GetIssueResponseChangelogHistoriesAuthorAvatarUrls]):
        display_name (Optional[str]): The display name of the user. Depending on the user’s privacy settings, this may
                return an alternative value.
        email_address (Optional[str]): The email address of the user. Depending on the user’s privacy settings, this may
                be returned as null.
        key (Optional[str]): This property is no longer available and will be removed from the documentation soon. See
                the [deprecation notice](https://developer.atlassian.com/cloud/jira/platform/deprecation-notice-user-privacy-
                api-migration-guide/) for details.
        name (Optional[str]): This property is no longer available and will be removed from the documentation soon. See
                the [deprecation notice](https://developer.atlassian.com/cloud/jira/platform/deprecation-notice-user-privacy-
                api-migration-guide/) for details.
        self_ (Optional[str]): The URL of the user
        time_zone (Optional[str]): The time zone specified in the user's profile. Depending on the user’s privacy
                settings, this may be returned as null.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    account_id: Optional[str] = Field(alias="accountId", default=None)
    account_type: Optional[str] = Field(alias="accountType", default=None)
    active: Optional[bool] = Field(alias="active", default=None)
    avatar_urls: Optional["GetIssueResponseChangelogHistoriesAuthorAvatarUrls"] = Field(
        alias="avatarUrls", default=None
    )
    display_name: Optional[str] = Field(alias="displayName", default=None)
    email_address: Optional[str] = Field(alias="emailAddress", default=None)
    key: Optional[str] = Field(alias="key", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    self_: Optional[str] = Field(alias="self", default=None)
    time_zone: Optional[str] = Field(alias="timeZone", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetIssueResponseChangelogHistoriesAuthor"], src_dict: Dict[str, Any]
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

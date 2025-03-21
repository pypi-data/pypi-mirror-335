from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.find_user_by_email_account_type import FindUserByEmailAccountType
from ..models.find_user_by_email_application_roles import (
    FindUserByEmailApplicationRoles,
)
from ..models.find_user_by_email_avatar_urls import FindUserByEmailAvatarUrls
from ..models.find_user_by_email_groups import FindUserByEmailGroups


class FindUserByEmail(BaseModel):
    """
    Attributes:
        account_id (Optional[str]): The account ID of the user, which uniquely identifies the user across all Atlassian
                products. For example, *5b10ac8d82e05b22cc7d4ef5*. Required in requests.
        account_type (Optional[FindUserByEmailAccountType]): The user account type. Can take the following values:

                 *  `atlassian` regular Atlassian user account
                 *  `app` system account used for Connect applications and OAuth to represent external systems
                 *  `customer` Jira Service Desk account representing an external service desk
        active (Optional[bool]): Whether the user is active.
        application_roles (Optional[FindUserByEmailApplicationRoles]):
        avatar_urls (Optional[FindUserByEmailAvatarUrls]):
        display_name (Optional[str]): The display name of the user. Depending on the user’s privacy setting, this may
                return an alternative value.
        email_address (Optional[str]): The email address of the user. Depending on the user’s privacy setting, this may
                be returned as null.
        expand (Optional[str]): Expand options that include additional user details in the response.
        groups (Optional[FindUserByEmailGroups]):
        key (Optional[str]): This property is no longer available and will be removed from the documentation soon. See
                the [deprecation notice](https://developer.atlassian.com/cloud/jira/platform/deprecation-notice-user-privacy-
                api-migration-guide/) for details.
        locale (Optional[str]): The locale of the user. Depending on the user’s privacy setting, this may be returned as
                null.
        name (Optional[str]): This property is no longer available and will be removed from the documentation soon. See
                the [deprecation notice](https://developer.atlassian.com/cloud/jira/platform/deprecation-notice-user-privacy-
                api-migration-guide/) for details.
        self_ (Optional[str]): The URL of the user.
        time_zone (Optional[str]): The time zone specified in the user's profile. Depending on the user’s privacy
                setting, this may be returned as null.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    account_id: Optional[str] = Field(alias="accountId", default=None)
    account_type: Optional["FindUserByEmailAccountType"] = Field(
        alias="accountType", default=None
    )
    active: Optional[bool] = Field(alias="active", default=None)
    application_roles: Optional["FindUserByEmailApplicationRoles"] = Field(
        alias="applicationRoles", default=None
    )
    avatar_urls: Optional["FindUserByEmailAvatarUrls"] = Field(
        alias="avatarUrls", default=None
    )
    display_name: Optional[str] = Field(alias="displayName", default=None)
    email_address: Optional[str] = Field(alias="emailAddress", default=None)
    expand: Optional[str] = Field(alias="expand", default=None)
    groups: Optional["FindUserByEmailGroups"] = Field(alias="groups", default=None)
    key: Optional[str] = Field(alias="key", default=None)
    locale: Optional[str] = Field(alias="locale", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    self_: Optional[str] = Field(alias="self", default=None)
    time_zone: Optional[str] = Field(alias="timeZone", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["FindUserByEmail"], src_dict: Dict[str, Any]):
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

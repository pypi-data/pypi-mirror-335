from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class FindUserByEmailApplicationRolesItemsArrayItemRef(BaseModel):
    """
    Attributes:
        default_groups (Optional[list[str]]):
        defined (Optional[bool]): Deprecated.
        groups (Optional[list[str]]):
        has_unlimited_seats (Optional[bool]):
        key (Optional[str]): The key of the application role.
        name (Optional[str]): The display name of the application role.
        number_of_seats (Optional[int]): The maximum count of users on your license.
        platform (Optional[bool]): Indicates if the application role belongs to Jira platform (`jira-core`).
        remaining_seats (Optional[int]): The count of users remaining on your license.
        selected_by_default (Optional[bool]): Determines whether this application role should be selected by default on
                user creation.
        user_count (Optional[int]): The number of users counting against your license.
        user_count_description (Optional[str]): The [type of users](https://confluence.atlassian.com/x/lRW3Ng) being
                counted against your license.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    default_groups: Optional[list[str]] = Field(alias="defaultGroups", default=None)
    defined: Optional[bool] = Field(alias="defined", default=None)
    groups: Optional[list[str]] = Field(alias="groups", default=None)
    has_unlimited_seats: Optional[bool] = Field(alias="hasUnlimitedSeats", default=None)
    key: Optional[str] = Field(alias="key", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    number_of_seats: Optional[int] = Field(alias="numberOfSeats", default=None)
    platform: Optional[bool] = Field(alias="platform", default=None)
    remaining_seats: Optional[int] = Field(alias="remainingSeats", default=None)
    selected_by_default: Optional[bool] = Field(alias="selectedByDefault", default=None)
    user_count: Optional[int] = Field(alias="userCount", default=None)
    user_count_description: Optional[str] = Field(
        alias="userCountDescription", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["FindUserByEmailApplicationRolesItemsArrayItemRef"],
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

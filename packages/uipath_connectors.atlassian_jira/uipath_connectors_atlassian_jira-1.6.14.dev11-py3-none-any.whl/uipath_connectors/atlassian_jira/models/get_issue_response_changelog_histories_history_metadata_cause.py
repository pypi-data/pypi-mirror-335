from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class GetIssueResponseChangelogHistoriesHistoryMetadataCause(BaseModel):
    """
    Attributes:
        avatar_url (Optional[str]): The URL to an avatar for the user or system associated with a history record
        display_name (Optional[str]): The display name of the user or system associated with a history record
        display_name_key (Optional[str]): The key of the display name of the user or system associated with a history
                record
        id (Optional[str]): The ID of the user or system associated with a history record
        type_ (Optional[str]): The type of the user or system associated with a history record
        url (Optional[str]): The URL of the user or system associated with a history record.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    avatar_url: Optional[str] = Field(alias="avatarUrl", default=None)
    display_name: Optional[str] = Field(alias="displayName", default=None)
    display_name_key: Optional[str] = Field(alias="displayNameKey", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    type_: Optional[str] = Field(alias="type", default=None)
    url: Optional[str] = Field(alias="url", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetIssueResponseChangelogHistoriesHistoryMetadataCause"],
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

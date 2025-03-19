from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class SearchIssuebyJQLFieldsIssuetype(BaseModel):
    """
    Attributes:
        avatar_id (Optional[int]):
        description (Optional[str]):
        entity_id (Optional[str]):
        hierarchy_level (Optional[int]):
        icon_url (Optional[str]):
        id (Optional[str]): The type of the issue (task, story, bug, epic, etc). Select one to enable custom fields.
        name (Optional[str]):
        self_ (Optional[str]):
        subtask (Optional[bool]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    avatar_id: Optional[int] = Field(alias="avatarId", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    entity_id: Optional[str] = Field(alias="entityId", default=None)
    hierarchy_level: Optional[int] = Field(alias="hierarchyLevel", default=None)
    icon_url: Optional[str] = Field(alias="iconUrl", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    self_: Optional[str] = Field(alias="self", default=None)
    subtask: Optional[bool] = Field(alias="subtask", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchIssuebyJQLFieldsIssuetype"], src_dict: Dict[str, Any]
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

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class GetIssueResponseTransitionsToStatusCategory(BaseModel):
    """
    Attributes:
        color_name (Optional[str]): The name of the color used to represent the status category
        id (Optional[int]): The ID of the status category
        key (Optional[str]): The key of the status category
        name (Optional[str]): The name of the status category
        self_ (Optional[str]): The URL of the status category
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    color_name: Optional[str] = Field(alias="colorName", default=None)
    id: Optional[int] = Field(alias="id", default=None)
    key: Optional[str] = Field(alias="key", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    self_: Optional[str] = Field(alias="self", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetIssueResponseTransitionsToStatusCategory"],
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

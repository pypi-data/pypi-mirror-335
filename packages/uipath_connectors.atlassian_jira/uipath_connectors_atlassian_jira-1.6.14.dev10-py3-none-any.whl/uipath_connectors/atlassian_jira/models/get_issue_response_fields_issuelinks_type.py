from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class GetIssueResponseFieldsIssuelinksType(BaseModel):
    """
    Attributes:
        id (Optional[str]): The ID representing the type of link between issues Example: 10000.
        inward (Optional[str]): The description of the inward relationship type Example: depends on.
        name (Optional[str]): The name describing the type of link between issues Example: Dependent.
        outward (Optional[str]): The description of the outward relationship type Example: is depended by.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: Optional[str] = Field(alias="id", default=None)
    inward: Optional[str] = Field(alias="inward", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    outward: Optional[str] = Field(alias="outward", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetIssueResponseFieldsIssuelinksType"], src_dict: Dict[str, Any]
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

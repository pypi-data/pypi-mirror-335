from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class GetIssueResponseFieldsReporterAvatarUrls(BaseModel):
    """
    Attributes:
        field_16x16 (Optional[str]):
        field_24x24 (Optional[str]):
        field_32x32 (Optional[str]):
        field_48x48 (Optional[str]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    field_16x16: Optional[str] = Field(alias="16x16", default=None)
    field_24x24: Optional[str] = Field(alias="24x24", default=None)
    field_32x32: Optional[str] = Field(alias="32x32", default=None)
    field_48x48: Optional[str] = Field(alias="48x48", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetIssueResponseFieldsReporterAvatarUrls"], src_dict: Dict[str, Any]
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

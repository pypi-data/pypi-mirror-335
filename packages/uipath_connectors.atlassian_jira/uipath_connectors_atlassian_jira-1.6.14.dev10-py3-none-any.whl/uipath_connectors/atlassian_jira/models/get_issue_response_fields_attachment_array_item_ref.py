from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_issue_response_fields_attachment_author import (
    GetIssueResponseFieldsAttachmentAuthor,
)
import datetime


class GetIssueResponseFieldsAttachmentArrayItemRef(BaseModel):
    """
    Attributes:
        author (Optional[GetIssueResponseFieldsAttachmentAuthor]):
        content (Optional[str]): The content of attachment
        created (Optional[datetime.datetime]): The created of attachment
        filename (Optional[str]): The file name of attachment
        id (Optional[str]): The ID of attachment
        mime_type (Optional[str]): The mime type of attachment
        self_ (Optional[str]): The self of attachment
        size (Optional[int]): The size of attachment
        thumbnail (Optional[str]): The thumbnail of attachment
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    author: Optional["GetIssueResponseFieldsAttachmentAuthor"] = Field(
        alias="author", default=None
    )
    content: Optional[str] = Field(alias="content", default=None)
    created: Optional[datetime.datetime] = Field(alias="created", default=None)
    filename: Optional[str] = Field(alias="filename", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    mime_type: Optional[str] = Field(alias="mimeType", default=None)
    self_: Optional[str] = Field(alias="self", default=None)
    size: Optional[int] = Field(alias="size", default=None)
    thumbnail: Optional[str] = Field(alias="thumbnail", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetIssueResponseFieldsAttachmentArrayItemRef"],
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

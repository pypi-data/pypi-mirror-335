from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.add_comment_response_author import AddCommentResponseAuthor
from ..models.add_comment_response_update_author import AddCommentResponseUpdateAuthor
from ..models.add_comment_response_visibility import AddCommentResponseVisibility
import datetime


class AddCommentResponse(BaseModel):
    """
    Attributes:
        body (str): Provide input for the comment using text
        author (Optional[AddCommentResponseAuthor]):
        created (Optional[datetime.datetime]): The Created Example: 2021-01-17T12:34:00.000+0000.
        id (Optional[str]): The ID of the new comment Example: 10000.
        self_ (Optional[str]): The Self Example: https://your-domain.atlassian.net/rest/api/3/issue/10010/comment/10000.
        update_author (Optional[AddCommentResponseUpdateAuthor]):
        updated (Optional[datetime.datetime]): The Updated Example: 2021-01-18T23:45:00.000+0000.
        visibility (Optional[AddCommentResponseVisibility]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    body: str = Field(alias="body")
    author: Optional["AddCommentResponseAuthor"] = Field(alias="author", default=None)
    created: Optional[datetime.datetime] = Field(alias="created", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    self_: Optional[str] = Field(alias="self", default=None)
    update_author: Optional["AddCommentResponseUpdateAuthor"] = Field(
        alias="updateAuthor", default=None
    )
    updated: Optional[datetime.datetime] = Field(alias="updated", default=None)
    visibility: Optional["AddCommentResponseVisibility"] = Field(
        alias="visibility", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["AddCommentResponse"], src_dict: Dict[str, Any]):
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

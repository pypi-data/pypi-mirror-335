from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_comments_author import GetCommentsAuthor
from ..models.get_comments_properties_array_item_ref import (
    GetCommentsPropertiesArrayItemRef,
)
from ..models.get_comments_update_author import GetCommentsUpdateAuthor
from ..models.get_comments_visibility import GetCommentsVisibility
import datetime


class GetComments(BaseModel):
    """
    Attributes:
        author (Optional[GetCommentsAuthor]):
        body (Optional[str]): Provide input for the comment using text
        created (Optional[datetime.datetime]): The date and time at which the comment was created.
        id (Optional[str]): The ID of the new comment.
        jsd_public (Optional[bool]): Whether the comment is visible in Jira Service Desk. Defaults to true when comments
                are created in the Jira Cloud Platform. This includes when the site doesn't use Jira Service Desk or the project
                isn't a Jira Service Desk project and, therefore, there is no Jira Service Desk for the issue to be visible on.
                To create a comment with its visibility in Jira Service Desk set to false, use the Jira Service Desk REST API
                [Create request comment](https://developer.atlassian.com/cloud/jira/service-desk/rest/#api-rest-servicedeskapi-
                request-issueIdOrKey-comment-post) operation.
        properties (Optional[list['GetCommentsPropertiesArrayItemRef']]):
        rendered_body (Optional[str]): The rendered version of the comment.
        self_ (Optional[str]): The URL of the comment.
        update_author (Optional[GetCommentsUpdateAuthor]):
        updated (Optional[datetime.datetime]): The date and time at which the comment was updated last.
        visibility (Optional[GetCommentsVisibility]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    author: Optional["GetCommentsAuthor"] = Field(alias="author", default=None)
    body: Optional[str] = Field(alias="body", default=None)
    created: Optional[datetime.datetime] = Field(alias="created", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    jsd_public: Optional[bool] = Field(alias="jsdPublic", default=None)
    properties: Optional[list["GetCommentsPropertiesArrayItemRef"]] = Field(
        alias="properties", default=None
    )
    rendered_body: Optional[str] = Field(alias="renderedBody", default=None)
    self_: Optional[str] = Field(alias="self", default=None)
    update_author: Optional["GetCommentsUpdateAuthor"] = Field(
        alias="updateAuthor", default=None
    )
    updated: Optional[datetime.datetime] = Field(alias="updated", default=None)
    visibility: Optional["GetCommentsVisibility"] = Field(
        alias="visibility", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetComments"], src_dict: Dict[str, Any]):
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

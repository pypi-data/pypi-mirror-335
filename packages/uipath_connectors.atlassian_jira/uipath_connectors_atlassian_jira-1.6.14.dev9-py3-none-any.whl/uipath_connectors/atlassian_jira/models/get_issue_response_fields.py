from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_issue_response_fields_aggregateprogress import (
    GetIssueResponseFieldsAggregateprogress,
)
from ..models.get_issue_response_fields_assignee import GetIssueResponseFieldsAssignee
from ..models.get_issue_response_fields_attachment_array_item_ref import (
    GetIssueResponseFieldsAttachmentArrayItemRef,
)
from ..models.get_issue_response_fields_components_array_item_ref import (
    GetIssueResponseFieldsComponentsArrayItemRef,
)
from ..models.get_issue_response_fields_creator import GetIssueResponseFieldsCreator
from ..models.get_issue_response_fields_fix_versions_array_item_ref import (
    GetIssueResponseFieldsFixVersionsArrayItemRef,
)
from ..models.get_issue_response_fields_issuelinks_array_item_ref import (
    GetIssueResponseFieldsIssuelinksArrayItemRef,
)
from ..models.get_issue_response_fields_issuetype import GetIssueResponseFieldsIssuetype
from ..models.get_issue_response_fields_parent import GetIssueResponseFieldsParent
from ..models.get_issue_response_fields_priority import GetIssueResponseFieldsPriority
from ..models.get_issue_response_fields_progress import GetIssueResponseFieldsProgress
from ..models.get_issue_response_fields_project import GetIssueResponseFieldsProject
from ..models.get_issue_response_fields_reporter import GetIssueResponseFieldsReporter
from ..models.get_issue_response_fields_security import GetIssueResponseFieldsSecurity
from ..models.get_issue_response_fields_status import GetIssueResponseFieldsStatus
from ..models.get_issue_response_fields_timetracking import (
    GetIssueResponseFieldsTimetracking,
)
from ..models.get_issue_response_fields_versions_array_item_ref import (
    GetIssueResponseFieldsVersionsArrayItemRef,
)
from ..models.get_issue_response_fields_votes import GetIssueResponseFieldsVotes
from ..models.get_issue_response_fields_watches import GetIssueResponseFieldsWatches
import datetime


class GetIssueResponseFields(BaseModel):
    """
    Attributes:
        aggregateprogress (Optional[GetIssueResponseFieldsAggregateprogress]):
        assignee (Optional[GetIssueResponseFieldsAssignee]):
        attachment (Optional[list['GetIssueResponseFieldsAttachmentArrayItemRef']]):
        components (Optional[list['GetIssueResponseFieldsComponentsArrayItemRef']]):
        created (Optional[datetime.datetime]):
        creator (Optional[GetIssueResponseFieldsCreator]):
        description (Optional[str]):
        duedate (Optional[datetime.datetime]):
        environment (Optional[str]):
        fix_versions (Optional[list['GetIssueResponseFieldsFixVersionsArrayItemRef']]):
        issuelinks (Optional[list['GetIssueResponseFieldsIssuelinksArrayItemRef']]):
        issuetype (Optional[GetIssueResponseFieldsIssuetype]):
        labels (Optional[list[str]]):
        parent (Optional[GetIssueResponseFieldsParent]):
        priority (Optional[GetIssueResponseFieldsPriority]):
        progress (Optional[GetIssueResponseFieldsProgress]):
        project (Optional[GetIssueResponseFieldsProject]):
        reporter (Optional[GetIssueResponseFieldsReporter]):
        security (Optional[GetIssueResponseFieldsSecurity]):
        status (Optional[GetIssueResponseFieldsStatus]):
        statuscategorychangedate (Optional[datetime.datetime]):
        summary (Optional[str]):
        timetracking (Optional[GetIssueResponseFieldsTimetracking]):
        updated (Optional[datetime.datetime]):
        versions (Optional[list['GetIssueResponseFieldsVersionsArrayItemRef']]):
        votes (Optional[GetIssueResponseFieldsVotes]):
        watches (Optional[GetIssueResponseFieldsWatches]):
        workratio (Optional[int]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    aggregateprogress: Optional["GetIssueResponseFieldsAggregateprogress"] = Field(
        alias="aggregateprogress", default=None
    )
    assignee: Optional["GetIssueResponseFieldsAssignee"] = Field(
        alias="assignee", default=None
    )
    attachment: Optional[list["GetIssueResponseFieldsAttachmentArrayItemRef"]] = Field(
        alias="attachment", default=None
    )
    components: Optional[list["GetIssueResponseFieldsComponentsArrayItemRef"]] = Field(
        alias="components", default=None
    )
    created: Optional[datetime.datetime] = Field(alias="created", default=None)
    creator: Optional["GetIssueResponseFieldsCreator"] = Field(
        alias="creator", default=None
    )
    description: Optional[str] = Field(alias="description", default=None)
    duedate: Optional[datetime.datetime] = Field(alias="duedate", default=None)
    environment: Optional[str] = Field(alias="environment", default=None)
    fix_versions: Optional[list["GetIssueResponseFieldsFixVersionsArrayItemRef"]] = (
        Field(alias="fixVersions", default=None)
    )
    issuelinks: Optional[list["GetIssueResponseFieldsIssuelinksArrayItemRef"]] = Field(
        alias="issuelinks", default=None
    )
    issuetype: Optional["GetIssueResponseFieldsIssuetype"] = Field(
        alias="issuetype", default=None
    )
    labels: Optional[list[str]] = Field(alias="labels", default=None)
    parent: Optional["GetIssueResponseFieldsParent"] = Field(
        alias="parent", default=None
    )
    priority: Optional["GetIssueResponseFieldsPriority"] = Field(
        alias="priority", default=None
    )
    progress: Optional["GetIssueResponseFieldsProgress"] = Field(
        alias="progress", default=None
    )
    project: Optional["GetIssueResponseFieldsProject"] = Field(
        alias="project", default=None
    )
    reporter: Optional["GetIssueResponseFieldsReporter"] = Field(
        alias="reporter", default=None
    )
    security: Optional["GetIssueResponseFieldsSecurity"] = Field(
        alias="security", default=None
    )
    status: Optional["GetIssueResponseFieldsStatus"] = Field(
        alias="status", default=None
    )
    statuscategorychangedate: Optional[datetime.datetime] = Field(
        alias="statuscategorychangedate", default=None
    )
    summary: Optional[str] = Field(alias="summary", default=None)
    timetracking: Optional["GetIssueResponseFieldsTimetracking"] = Field(
        alias="timetracking", default=None
    )
    updated: Optional[datetime.datetime] = Field(alias="updated", default=None)
    versions: Optional[list["GetIssueResponseFieldsVersionsArrayItemRef"]] = Field(
        alias="versions", default=None
    )
    votes: Optional["GetIssueResponseFieldsVotes"] = Field(alias="votes", default=None)
    watches: Optional["GetIssueResponseFieldsWatches"] = Field(
        alias="watches", default=None
    )
    workratio: Optional[int] = Field(alias="workratio", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetIssueResponseFields"], src_dict: Dict[str, Any]):
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

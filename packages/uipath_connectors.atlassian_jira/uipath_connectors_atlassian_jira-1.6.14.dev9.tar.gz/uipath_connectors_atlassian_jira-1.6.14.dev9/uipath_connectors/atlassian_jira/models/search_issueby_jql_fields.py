from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_issueby_jql_fields_aggregateprogress import (
    SearchIssuebyJQLFieldsAggregateprogress,
)
from ..models.search_issueby_jql_fields_assignee import SearchIssuebyJQLFieldsAssignee
from ..models.search_issueby_jql_fields_components_array_item_ref import (
    SearchIssuebyJQLFieldsComponentsArrayItemRef,
)
from ..models.search_issueby_jql_fields_creator import SearchIssuebyJQLFieldsCreator
from ..models.search_issueby_jql_fields_fix_versions_array_item_ref import (
    SearchIssuebyJQLFieldsFixVersionsArrayItemRef,
)
from ..models.search_issueby_jql_fields_issuetype import SearchIssuebyJQLFieldsIssuetype
from ..models.search_issueby_jql_fields_priority import SearchIssuebyJQLFieldsPriority
from ..models.search_issueby_jql_fields_progress import SearchIssuebyJQLFieldsProgress
from ..models.search_issueby_jql_fields_project import SearchIssuebyJQLFieldsProject
from ..models.search_issueby_jql_fields_reporter import SearchIssuebyJQLFieldsReporter
from ..models.search_issueby_jql_fields_security import SearchIssuebyJQLFieldsSecurity
from ..models.search_issueby_jql_fields_status import SearchIssuebyJQLFieldsStatus
from ..models.search_issueby_jql_fields_timetracking import (
    SearchIssuebyJQLFieldsTimetracking,
)
from ..models.search_issueby_jql_fields_versions_array_item_ref import (
    SearchIssuebyJQLFieldsVersionsArrayItemRef,
)
from ..models.search_issueby_jql_fields_votes import SearchIssuebyJQLFieldsVotes
from ..models.search_issueby_jql_fields_watches import SearchIssuebyJQLFieldsWatches
import datetime


class SearchIssuebyJQLFields(BaseModel):
    """
    Attributes:
        aggregateprogress (Optional[SearchIssuebyJQLFieldsAggregateprogress]):
        assignee (Optional[SearchIssuebyJQLFieldsAssignee]):
        components (Optional[list['SearchIssuebyJQLFieldsComponentsArrayItemRef']]):
        created (Optional[datetime.datetime]):
        creator (Optional[SearchIssuebyJQLFieldsCreator]):
        description (Optional[str]):
        duedate (Optional[datetime.datetime]):
        environment (Optional[str]):
        fix_versions (Optional[list['SearchIssuebyJQLFieldsFixVersionsArrayItemRef']]):
        issuetype (Optional[SearchIssuebyJQLFieldsIssuetype]):
        labels (Optional[list[str]]):
        priority (Optional[SearchIssuebyJQLFieldsPriority]):
        progress (Optional[SearchIssuebyJQLFieldsProgress]):
        project (Optional[SearchIssuebyJQLFieldsProject]):
        reporter (Optional[SearchIssuebyJQLFieldsReporter]):
        security (Optional[SearchIssuebyJQLFieldsSecurity]):
        status (Optional[SearchIssuebyJQLFieldsStatus]):
        statuscategorychangedate (Optional[datetime.datetime]):
        summary (Optional[str]):
        timetracking (Optional[SearchIssuebyJQLFieldsTimetracking]):
        updated (Optional[datetime.datetime]):
        versions (Optional[list['SearchIssuebyJQLFieldsVersionsArrayItemRef']]):
        votes (Optional[SearchIssuebyJQLFieldsVotes]):
        watches (Optional[SearchIssuebyJQLFieldsWatches]):
        workratio (Optional[int]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    aggregateprogress: Optional["SearchIssuebyJQLFieldsAggregateprogress"] = Field(
        alias="aggregateprogress", default=None
    )
    assignee: Optional["SearchIssuebyJQLFieldsAssignee"] = Field(
        alias="assignee", default=None
    )
    components: Optional[list["SearchIssuebyJQLFieldsComponentsArrayItemRef"]] = Field(
        alias="components", default=None
    )
    created: Optional[datetime.datetime] = Field(alias="created", default=None)
    creator: Optional["SearchIssuebyJQLFieldsCreator"] = Field(
        alias="creator", default=None
    )
    description: Optional[str] = Field(alias="description", default=None)
    duedate: Optional[datetime.datetime] = Field(alias="duedate", default=None)
    environment: Optional[str] = Field(alias="environment", default=None)
    fix_versions: Optional[list["SearchIssuebyJQLFieldsFixVersionsArrayItemRef"]] = (
        Field(alias="fixVersions", default=None)
    )
    issuetype: Optional["SearchIssuebyJQLFieldsIssuetype"] = Field(
        alias="issuetype", default=None
    )
    labels: Optional[list[str]] = Field(alias="labels", default=None)
    priority: Optional["SearchIssuebyJQLFieldsPriority"] = Field(
        alias="priority", default=None
    )
    progress: Optional["SearchIssuebyJQLFieldsProgress"] = Field(
        alias="progress", default=None
    )
    project: Optional["SearchIssuebyJQLFieldsProject"] = Field(
        alias="project", default=None
    )
    reporter: Optional["SearchIssuebyJQLFieldsReporter"] = Field(
        alias="reporter", default=None
    )
    security: Optional["SearchIssuebyJQLFieldsSecurity"] = Field(
        alias="security", default=None
    )
    status: Optional["SearchIssuebyJQLFieldsStatus"] = Field(
        alias="status", default=None
    )
    statuscategorychangedate: Optional[datetime.datetime] = Field(
        alias="statuscategorychangedate", default=None
    )
    summary: Optional[str] = Field(alias="summary", default=None)
    timetracking: Optional["SearchIssuebyJQLFieldsTimetracking"] = Field(
        alias="timetracking", default=None
    )
    updated: Optional[datetime.datetime] = Field(alias="updated", default=None)
    versions: Optional[list["SearchIssuebyJQLFieldsVersionsArrayItemRef"]] = Field(
        alias="versions", default=None
    )
    votes: Optional["SearchIssuebyJQLFieldsVotes"] = Field(alias="votes", default=None)
    watches: Optional["SearchIssuebyJQLFieldsWatches"] = Field(
        alias="watches", default=None
    )
    workratio: Optional[int] = Field(alias="workratio", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchIssuebyJQLFields"], src_dict: Dict[str, Any]):
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

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class GetInstanceInfoResponse(BaseModel):
    """
    Attributes:
        base_url (Optional[str]): The base URL of the Jira instance
        build_date (Optional[datetime.datetime]): The timestamp when the Jira version was built.
        build_number (Optional[int]): The build number of the Jira version.
        deployment_type (Optional[str]): The type of server deployment. This is always returned as *Cloud*.
        scm_info (Optional[str]): The unique identifier of the Jira version.
        server_time (Optional[datetime.datetime]): The time in Jira when this request was responded to.
        server_title (Optional[str]): The name of the Jira instance.
        site_url (Optional[str]): The site URL of the Jira instance
        version (Optional[str]): The version of Jira.
        version_numbers (Optional[list[int]]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    base_url: Optional[str] = Field(alias="baseUrl", default=None)
    build_date: Optional[datetime.datetime] = Field(alias="buildDate", default=None)
    build_number: Optional[int] = Field(alias="buildNumber", default=None)
    deployment_type: Optional[str] = Field(alias="deploymentType", default=None)
    scm_info: Optional[str] = Field(alias="scmInfo", default=None)
    server_time: Optional[datetime.datetime] = Field(alias="serverTime", default=None)
    server_title: Optional[str] = Field(alias="serverTitle", default=None)
    site_url: Optional[str] = Field(alias="siteUrl", default=None)
    version: Optional[str] = Field(alias="version", default=None)
    version_numbers: Optional[list[int]] = Field(alias="versionNumbers", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetInstanceInfoResponse"], src_dict: Dict[str, Any]):
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

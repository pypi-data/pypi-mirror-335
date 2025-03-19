from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_issueby_jql_transitions_fields import (
    SearchIssuebyJQLTransitionsFields,
)
from ..models.search_issueby_jql_transitions_to import SearchIssuebyJQLTransitionsTo


class SearchIssuebyJQLTransitionsArrayItemRef(BaseModel):
    """
    Attributes:
        expand (Optional[str]): Expand options that include additional transition details in the response.
        fields (Optional[SearchIssuebyJQLTransitionsFields]):
        has_screen (Optional[bool]): Whether there is a screen associated with the issue transition.
        id (Optional[str]): The ID of the issue transition. Required when specifying a transition to undertake.
        is_available (Optional[bool]): Whether the transition is available to be performed.
        is_conditional (Optional[bool]): Whether the issue has to meet criteria before the issue transition is applied.
        is_global (Optional[bool]): Whether the issue transition is global, that is, the transition is applied to issues
                regardless of their status.
        is_initial (Optional[bool]): Whether this is the initial issue transition for the workflow.
        looped (Optional[bool]):
        name (Optional[str]): The name of the issue transition.
        to (Optional[SearchIssuebyJQLTransitionsTo]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    expand: Optional[str] = Field(alias="expand", default=None)
    fields: Optional["SearchIssuebyJQLTransitionsFields"] = Field(
        alias="fields", default=None
    )
    has_screen: Optional[bool] = Field(alias="hasScreen", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    is_available: Optional[bool] = Field(alias="isAvailable", default=None)
    is_conditional: Optional[bool] = Field(alias="isConditional", default=None)
    is_global: Optional[bool] = Field(alias="isGlobal", default=None)
    is_initial: Optional[bool] = Field(alias="isInitial", default=None)
    looped: Optional[bool] = Field(alias="looped", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    to: Optional["SearchIssuebyJQLTransitionsTo"] = Field(alias="to", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchIssuebyJQLTransitionsArrayItemRef"], src_dict: Dict[str, Any]
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

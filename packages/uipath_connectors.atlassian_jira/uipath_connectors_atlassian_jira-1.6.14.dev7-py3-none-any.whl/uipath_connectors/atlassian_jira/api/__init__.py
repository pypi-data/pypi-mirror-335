from .curated_get_issue import (
    get_issue as _get_issue,
    get_issue_async as _get_issue_async,
)
from ..models.default_error import DefaultError
from ..models.get_issue_response import GetIssueResponse
from typing import cast
from .curated_issue_status_update import (
    transition_issue as _transition_issue,
    transition_issue_async as _transition_issue_async,
)
from ..models.transition_issue_request import TransitionIssueRequest
from .curated_issue_assignee import (
    update_issue_assignee as _update_issue_assignee,
    update_issue_assignee_async as _update_issue_assignee_async,
)
from ..models.update_issue_assignee_request import UpdateIssueAssigneeRequest
from .server_info import (
    get_instance_info as _get_instance_info,
    get_instance_info_async as _get_instance_info_async,
)
from ..models.get_instance_info_response import GetInstanceInfoResponse
from .curated_create_issue import (
    create_issue as _create_issue,
    create_issue_async as _create_issue_async,
)
from ..models.create_issue_request import CreateIssueRequest
from ..models.create_issue_response import CreateIssueResponse
from .issue_attachments import (
    add_attachment as _add_attachment,
    add_attachment_async as _add_attachment_async,
)
from ..models.add_attachment_body import AddAttachmentBody
from ..models.add_attachment_response import AddAttachmentResponse
from .issue_comment import (
    get_comments as _get_comments,
    get_comments_async as _get_comments_async,
)
from ..models.get_comments import GetComments
from .curated_add_comment import (
    add_comment as _add_comment,
    add_comment_async as _add_comment_async,
)
from ..models.add_comment_request import AddCommentRequest
from ..models.add_comment_response import AddCommentResponse
from .search_user import (
    find_user_by_email as _find_user_by_email,
    find_user_by_email_async as _find_user_by_email_async,
)
from ..models.find_user_by_email import FindUserByEmail
from .curated_download_issue_attachment import (
    download_issue_attachment as _download_issue_attachment,
    download_issue_attachment_async as _download_issue_attachment_async,
)
from ..types import File, FileJsonType
from io import BytesIO
from .issue_search_get import (
    search_issueby_jql as _search_issueby_jql,
    search_issueby_jql_async as _search_issueby_jql_async,
)
from ..models.search_issueby_jql import SearchIssuebyJQL
from .curated_edit_issue import (
    upsert_issue as _upsert_issue,
    upsert_issue_async as _upsert_issue_async,
)

from pydantic import Field
from typing import Any, Optional, Union

from ..client import Client
import httpx


class AtlassianJira:
    def __init__(self, *, instance_id: str, client: httpx.Client):
        base_url = str(client.base_url).rstrip("/")
        new_headers = {
            k: v for k, v in client.headers.items() if k not in ["content-type"]
        }
        new_client = httpx.Client(
            base_url=base_url + f"/elements_/v3/element/instances/{instance_id}",
            headers=new_headers,
            timeout=100,
        )
        new_client_async = httpx.AsyncClient(
            base_url=base_url + f"/elements_/v3/element/instances/{instance_id}",
            headers=new_headers,
            timeout=100,
        )
        self.client = (
            Client(
                base_url="",  # this will be overridden by the base_url in the Client constructor
            )
            .set_httpx_client(new_client)
            .set_async_httpx_client(new_client_async)
        )

    def get_issue(
        self,
        issue_id: str,
        issue_id_lookup: Any,
        *,
        issuetype: str,
        issuetype_lookup: Any,
        project: str,
        project_lookup: Any,
    ) -> Optional[Union[DefaultError, GetIssueResponse]]:
        return _get_issue(
            client=self.client,
            issue_id=issue_id,
            issue_id_lookup=issue_id_lookup,
            issuetype=issuetype,
            issuetype_lookup=issuetype_lookup,
            project=project,
            project_lookup=project_lookup,
        )

    async def get_issue_async(
        self,
        issue_id: str,
        issue_id_lookup: Any,
        *,
        issuetype: str,
        issuetype_lookup: Any,
        project: str,
        project_lookup: Any,
    ) -> Optional[Union[DefaultError, GetIssueResponse]]:
        return await _get_issue_async(
            client=self.client,
            issue_id=issue_id,
            issue_id_lookup=issue_id_lookup,
            issuetype=issuetype,
            issuetype_lookup=issuetype_lookup,
            project=project,
            project_lookup=project_lookup,
        )

    def transition_issue(
        self,
        issue_id_or_key: str,
        issue_id_or_key_lookup: Any,
        *,
        body: TransitionIssueRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return _transition_issue(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            issue_id_or_key_lookup=issue_id_or_key_lookup,
            body=body,
        )

    async def transition_issue_async(
        self,
        issue_id_or_key: str,
        issue_id_or_key_lookup: Any,
        *,
        body: TransitionIssueRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _transition_issue_async(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            issue_id_or_key_lookup=issue_id_or_key_lookup,
            body=body,
        )

    def update_issue_assignee(
        self,
        issue_id_or_key: str,
        issue_id_or_key_lookup: Any,
        *,
        body: UpdateIssueAssigneeRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return _update_issue_assignee(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            issue_id_or_key_lookup=issue_id_or_key_lookup,
            body=body,
        )

    async def update_issue_assignee_async(
        self,
        issue_id_or_key: str,
        issue_id_or_key_lookup: Any,
        *,
        body: UpdateIssueAssigneeRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _update_issue_assignee_async(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            issue_id_or_key_lookup=issue_id_or_key_lookup,
            body=body,
        )

    def get_instance_info(
        self,
    ) -> Optional[Union[DefaultError, GetInstanceInfoResponse]]:
        return _get_instance_info(
            client=self.client,
        )

    async def get_instance_info_async(
        self,
    ) -> Optional[Union[DefaultError, GetInstanceInfoResponse]]:
        return await _get_instance_info_async(
            client=self.client,
        )

    def create_issue(
        self,
        *,
        body: CreateIssueRequest,
    ) -> Optional[Union[CreateIssueResponse, DefaultError]]:
        return _create_issue(
            client=self.client,
            body=body,
        )

    async def create_issue_async(
        self,
        *,
        body: CreateIssueRequest,
    ) -> Optional[Union[CreateIssueResponse, DefaultError]]:
        return await _create_issue_async(
            client=self.client,
            body=body,
        )

    def add_attachment(
        self,
        issue_id_or_key: str,
        issue_id_or_key_lookup: Any,
        *,
        body: AddAttachmentBody,
    ) -> Optional[Union[AddAttachmentResponse, DefaultError]]:
        return _add_attachment(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            issue_id_or_key_lookup=issue_id_or_key_lookup,
            body=body,
        )

    async def add_attachment_async(
        self,
        issue_id_or_key: str,
        issue_id_or_key_lookup: Any,
        *,
        body: AddAttachmentBody,
    ) -> Optional[Union[AddAttachmentResponse, DefaultError]]:
        return await _add_attachment_async(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            issue_id_or_key_lookup=issue_id_or_key_lookup,
            body=body,
        )

    def get_comments(
        self,
        issue_id_or_key: str,
        issue_id_or_key_lookup: Any,
        *,
        expand: Optional[str] = None,
        expand_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        order_by: Optional[str] = None,
        order_by_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        where: Optional[str] = None,
        where_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetComments"]]]:
        return _get_comments(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            issue_id_or_key_lookup=issue_id_or_key_lookup,
            expand=expand,
            expand_lookup=expand_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            order_by=order_by,
            order_by_lookup=order_by_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            where=where,
            where_lookup=where_lookup,
        )

    async def get_comments_async(
        self,
        issue_id_or_key: str,
        issue_id_or_key_lookup: Any,
        *,
        expand: Optional[str] = None,
        expand_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        order_by: Optional[str] = None,
        order_by_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        where: Optional[str] = None,
        where_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetComments"]]]:
        return await _get_comments_async(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            issue_id_or_key_lookup=issue_id_or_key_lookup,
            expand=expand,
            expand_lookup=expand_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            order_by=order_by,
            order_by_lookup=order_by_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            where=where,
            where_lookup=where_lookup,
        )

    def add_comment(
        self,
        issue_id_or_key: str,
        issue_id_or_key_lookup: Any,
        *,
        body: AddCommentRequest,
        expand: Optional[str] = None,
        expand_lookup: Any,
    ) -> Optional[Union[AddCommentResponse, DefaultError]]:
        return _add_comment(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            issue_id_or_key_lookup=issue_id_or_key_lookup,
            body=body,
            expand=expand,
            expand_lookup=expand_lookup,
        )

    async def add_comment_async(
        self,
        issue_id_or_key: str,
        issue_id_or_key_lookup: Any,
        *,
        body: AddCommentRequest,
        expand: Optional[str] = None,
        expand_lookup: Any,
    ) -> Optional[Union[AddCommentResponse, DefaultError]]:
        return await _add_comment_async(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            issue_id_or_key_lookup=issue_id_or_key_lookup,
            body=body,
            expand=expand,
            expand_lookup=expand_lookup,
        )

    def find_user_by_email(
        self,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        username: Optional[str] = None,
        username_lookup: Any,
    ) -> Optional[Union[DefaultError, list["FindUserByEmail"]]]:
        return _find_user_by_email(
            client=self.client,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            username=username,
            username_lookup=username_lookup,
        )

    async def find_user_by_email_async(
        self,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        username: Optional[str] = None,
        username_lookup: Any,
    ) -> Optional[Union[DefaultError, list["FindUserByEmail"]]]:
        return await _find_user_by_email_async(
            client=self.client,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            username=username,
            username_lookup=username_lookup,
        )

    def download_issue_attachment(
        self,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[DefaultError, File]]:
        return _download_issue_attachment(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
        )

    async def download_issue_attachment_async(
        self,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[DefaultError, File]]:
        return await _download_issue_attachment_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
        )

    def search_issueby_jql(
        self,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        jql: Optional[str] = None,
        jql_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        where: Optional[str] = None,
        where_lookup: Any,
    ) -> Optional[Union[DefaultError, list["SearchIssuebyJQL"]]]:
        return _search_issueby_jql(
            client=self.client,
            fields=fields,
            fields_lookup=fields_lookup,
            jql=jql,
            jql_lookup=jql_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            where=where,
            where_lookup=where_lookup,
        )

    async def search_issueby_jql_async(
        self,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        jql: Optional[str] = None,
        jql_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        where: Optional[str] = None,
        where_lookup: Any,
    ) -> Optional[Union[DefaultError, list["SearchIssuebyJQL"]]]:
        return await _search_issueby_jql_async(
            client=self.client,
            fields=fields,
            fields_lookup=fields_lookup,
            jql=jql,
            jql_lookup=jql_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            where=where,
            where_lookup=where_lookup,
        )

    def upsert_issue(
        self,
        issue_id_or_key: str,
        issue_id_or_key_lookup: Any,
        *,
        issuetype: str,
        issuetype_lookup: Any,
        project: str,
        project_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _upsert_issue(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            issue_id_or_key_lookup=issue_id_or_key_lookup,
            issuetype=issuetype,
            issuetype_lookup=issuetype_lookup,
            project=project,
            project_lookup=project_lookup,
        )

    async def upsert_issue_async(
        self,
        issue_id_or_key: str,
        issue_id_or_key_lookup: Any,
        *,
        issuetype: str,
        issuetype_lookup: Any,
        project: str,
        project_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _upsert_issue_async(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            issue_id_or_key_lookup=issue_id_or_key_lookup,
            issuetype=issuetype,
            issuetype_lookup=issuetype_lookup,
            project=project,
            project_lookup=project_lookup,
        )

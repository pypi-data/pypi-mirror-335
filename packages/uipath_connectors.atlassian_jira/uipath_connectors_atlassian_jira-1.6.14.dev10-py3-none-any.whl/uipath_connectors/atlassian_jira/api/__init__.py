from .issue_attachments import (
    add_attachment as _add_attachment,
    add_attachment_async as _add_attachment_async,
)
from ..models.add_attachment_body import AddAttachmentBody
from ..models.add_attachment_response import AddAttachmentResponse
from ..models.default_error import DefaultError
from typing import cast
from .curated_add_comment import (
    add_comment as _add_comment,
    add_comment_async as _add_comment_async,
)
from ..models.add_comment_request import AddCommentRequest
from ..models.add_comment_response import AddCommentResponse
from .curated_create_issue import (
    create_issue as _create_issue,
    create_issue_async as _create_issue_async,
)
from ..models.create_issue_request import CreateIssueRequest
from ..models.create_issue_response import CreateIssueResponse
from .curated_download_issue_attachment import (
    download_issue_attachment as _download_issue_attachment,
    download_issue_attachment_async as _download_issue_attachment_async,
)
from ..models.download_issue_attachment_response import DownloadIssueAttachmentResponse
from ..types import File
from io import BytesIO
from .search_user import (
    find_user_by_email as _find_user_by_email,
    find_user_by_email_async as _find_user_by_email_async,
)
from ..models.find_user_by_email import FindUserByEmail
from .issue_comment import (
    get_comments as _get_comments,
    get_comments_async as _get_comments_async,
)
from ..models.get_comments import GetComments
from .server_info import (
    get_instance_info as _get_instance_info,
    get_instance_info_async as _get_instance_info_async,
)
from ..models.get_instance_info_response import GetInstanceInfoResponse
from .curated_get_issue import (
    get_issue as _get_issue,
    get_issue_async as _get_issue_async,
)
from ..models.get_issue_response import GetIssueResponse
from .issue_search_get import (
    search_issueby_jql as _search_issueby_jql,
    search_issueby_jql_async as _search_issueby_jql_async,
)
from ..models.search_issueby_jql import SearchIssuebyJQL
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

    def add_comment(
        self,
        issue_id_or_key: str,
        issue_id_or_key_lookup: Any,
        *,
        body: AddCommentRequest,
        expand: Optional[str] = None,
    ) -> Optional[Union[AddCommentResponse, DefaultError]]:
        return _add_comment(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            issue_id_or_key_lookup=issue_id_or_key_lookup,
            body=body,
            expand=expand,
        )

    async def add_comment_async(
        self,
        issue_id_or_key: str,
        issue_id_or_key_lookup: Any,
        *,
        body: AddCommentRequest,
        expand: Optional[str] = None,
    ) -> Optional[Union[AddCommentResponse, DefaultError]]:
        return await _add_comment_async(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            issue_id_or_key_lookup=issue_id_or_key_lookup,
            body=body,
            expand=expand,
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

    def download_issue_attachment(
        self,
        id: str,
    ) -> Optional[Union[DefaultError, File]]:
        return _download_issue_attachment(
            client=self.client,
            id=id,
        )

    async def download_issue_attachment_async(
        self,
        id: str,
    ) -> Optional[Union[DefaultError, File]]:
        return await _download_issue_attachment_async(
            client=self.client,
            id=id,
        )

    def find_user_by_email(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        username: str,
    ) -> Optional[Union[DefaultError, list["FindUserByEmail"]]]:
        return _find_user_by_email(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            username=username,
        )

    async def find_user_by_email_async(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        username: str,
    ) -> Optional[Union[DefaultError, list["FindUserByEmail"]]]:
        return await _find_user_by_email_async(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            username=username,
        )

    def get_comments(
        self,
        issue_id_or_key: str,
        issue_id_or_key_lookup: Any,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        order_by: Optional[str] = None,
        expand: Optional[str] = None,
        where: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["GetComments"]]]:
        return _get_comments(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            issue_id_or_key_lookup=issue_id_or_key_lookup,
            page_size=page_size,
            next_page=next_page,
            order_by=order_by,
            expand=expand,
            where=where,
            fields=fields,
        )

    async def get_comments_async(
        self,
        issue_id_or_key: str,
        issue_id_or_key_lookup: Any,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        order_by: Optional[str] = None,
        expand: Optional[str] = None,
        where: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["GetComments"]]]:
        return await _get_comments_async(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            issue_id_or_key_lookup=issue_id_or_key_lookup,
            page_size=page_size,
            next_page=next_page,
            order_by=order_by,
            expand=expand,
            where=where,
            fields=fields,
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

    def get_issue(
        self,
        issue_id: str,
        *,
        project: str,
        project_lookup: Any,
        issuetype: str,
    ) -> Optional[Union[DefaultError, GetIssueResponse]]:
        return _get_issue(
            client=self.client,
            issue_id=issue_id,
            project=project,
            project_lookup=project_lookup,
            issuetype=issuetype,
        )

    async def get_issue_async(
        self,
        issue_id: str,
        *,
        project: str,
        project_lookup: Any,
        issuetype: str,
    ) -> Optional[Union[DefaultError, GetIssueResponse]]:
        return await _get_issue_async(
            client=self.client,
            issue_id=issue_id,
            project=project,
            project_lookup=project_lookup,
            issuetype=issuetype,
        )

    def search_issueby_jql(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        jql: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["SearchIssuebyJQL"]]]:
        return _search_issueby_jql(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            jql=jql,
        )

    async def search_issueby_jql_async(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        jql: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["SearchIssuebyJQL"]]]:
        return await _search_issueby_jql_async(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            jql=jql,
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
        *,
        body: UpdateIssueAssigneeRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return _update_issue_assignee(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            body=body,
        )

    async def update_issue_assignee_async(
        self,
        issue_id_or_key: str,
        *,
        body: UpdateIssueAssigneeRequest,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _update_issue_assignee_async(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            body=body,
        )

    def upsert_issue(
        self,
        issue_id_or_key: str,
        *,
        project: str,
        project_lookup: Any,
        issuetype: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return _upsert_issue(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            project=project,
            project_lookup=project_lookup,
            issuetype=issuetype,
        )

    async def upsert_issue_async(
        self,
        issue_id_or_key: str,
        *,
        project: str,
        project_lookup: Any,
        issuetype: str,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _upsert_issue_async(
            client=self.client,
            issue_id_or_key=issue_id_or_key,
            project=project,
            project_lookup=project_lookup,
            issuetype=issuetype,
        )

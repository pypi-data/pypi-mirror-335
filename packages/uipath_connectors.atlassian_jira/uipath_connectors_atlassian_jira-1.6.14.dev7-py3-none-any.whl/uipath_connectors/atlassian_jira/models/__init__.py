"""Contains all the data models used in inputs/outputs"""

from .add_attachment_body import AddAttachmentBody
from .add_attachment_response import AddAttachmentResponse
from .add_attachment_response_author import AddAttachmentResponseAuthor
from .add_attachment_response_author_avatar_urls import (
    AddAttachmentResponseAuthorAvatarUrls,
)
from .add_comment_request import AddCommentRequest
from .add_comment_response import AddCommentResponse
from .add_comment_response_author import AddCommentResponseAuthor
from .add_comment_response_update_author import AddCommentResponseUpdateAuthor
from .add_comment_response_visibility import AddCommentResponseVisibility
from .create_issue_request import CreateIssueRequest
from .create_issue_request_fields import CreateIssueRequestFields
from .create_issue_request_fields_issuetype import CreateIssueRequestFieldsIssuetype
from .create_issue_request_fields_project import CreateIssueRequestFieldsProject
from .create_issue_response import CreateIssueResponse
from .create_issue_response_fields import CreateIssueResponseFields
from .create_issue_response_fields_issuetype import CreateIssueResponseFieldsIssuetype
from .default_error import DefaultError
from .find_user_by_email import FindUserByEmail
from .find_user_by_email_account_type import FindUserByEmailAccountType
from .find_user_by_email_application_roles import FindUserByEmailApplicationRoles
from .find_user_by_email_application_roles_items_array_item_ref import (
    FindUserByEmailApplicationRolesItemsArrayItemRef,
)
from .find_user_by_email_avatar_urls import FindUserByEmailAvatarUrls
from .find_user_by_email_groups import FindUserByEmailGroups
from .find_user_by_email_groups_items_array_item_ref import (
    FindUserByEmailGroupsItemsArrayItemRef,
)
from .get_comments import GetComments
from .get_comments_author import GetCommentsAuthor
from .get_comments_author_avatar_urls import GetCommentsAuthorAvatarUrls
from .get_comments_properties_array_item_ref import GetCommentsPropertiesArrayItemRef
from .get_comments_update_author import GetCommentsUpdateAuthor
from .get_comments_update_author_avatar_urls import GetCommentsUpdateAuthorAvatarUrls
from .get_comments_visibility import GetCommentsVisibility
from .get_comments_visibility_visibility_type import GetCommentsVisibilityVisibilityType
from .get_instance_info_response import GetInstanceInfoResponse
from .get_issue_response import GetIssueResponse
from .get_issue_response_changelog import GetIssueResponseChangelog
from .get_issue_response_changelog_histories_array_item_ref import (
    GetIssueResponseChangelogHistoriesArrayItemRef,
)
from .get_issue_response_changelog_histories_author import (
    GetIssueResponseChangelogHistoriesAuthor,
)
from .get_issue_response_changelog_histories_author_avatar_urls import (
    GetIssueResponseChangelogHistoriesAuthorAvatarUrls,
)
from .get_issue_response_changelog_histories_history_metadata import (
    GetIssueResponseChangelogHistoriesHistoryMetadata,
)
from .get_issue_response_changelog_histories_history_metadata_actor import (
    GetIssueResponseChangelogHistoriesHistoryMetadataActor,
)
from .get_issue_response_changelog_histories_history_metadata_cause import (
    GetIssueResponseChangelogHistoriesHistoryMetadataCause,
)
from .get_issue_response_changelog_histories_history_metadata_generator import (
    GetIssueResponseChangelogHistoriesHistoryMetadataGenerator,
)
from .get_issue_response_changelog_histories_items_array_item_ref import (
    GetIssueResponseChangelogHistoriesItemsArrayItemRef,
)
from .get_issue_response_editmeta import GetIssueResponseEditmeta
from .get_issue_response_editmeta_fields import GetIssueResponseEditmetaFields
from .get_issue_response_editmeta_fields_schema import (
    GetIssueResponseEditmetaFieldsSchema,
)
from .get_issue_response_fields import GetIssueResponseFields
from .get_issue_response_fields_aggregateprogress import (
    GetIssueResponseFieldsAggregateprogress,
)
from .get_issue_response_fields_assignee import GetIssueResponseFieldsAssignee
from .get_issue_response_fields_assignee_avatar_urls import (
    GetIssueResponseFieldsAssigneeAvatarUrls,
)
from .get_issue_response_fields_attachment_array_item_ref import (
    GetIssueResponseFieldsAttachmentArrayItemRef,
)
from .get_issue_response_fields_attachment_author import (
    GetIssueResponseFieldsAttachmentAuthor,
)
from .get_issue_response_fields_attachment_author_avatar_urls import (
    GetIssueResponseFieldsAttachmentAuthorAvatarUrls,
)
from .get_issue_response_fields_components_array_item_ref import (
    GetIssueResponseFieldsComponentsArrayItemRef,
)
from .get_issue_response_fields_creator import GetIssueResponseFieldsCreator
from .get_issue_response_fields_creator_avatar_urls import (
    GetIssueResponseFieldsCreatorAvatarUrls,
)
from .get_issue_response_fields_fix_versions_array_item_ref import (
    GetIssueResponseFieldsFixVersionsArrayItemRef,
)
from .get_issue_response_fields_issuelinks_array_item_ref import (
    GetIssueResponseFieldsIssuelinksArrayItemRef,
)
from .get_issue_response_fields_issuelinks_inward_issue import (
    GetIssueResponseFieldsIssuelinksInwardIssue,
)
from .get_issue_response_fields_issuelinks_inward_issue_fields import (
    GetIssueResponseFieldsIssuelinksInwardIssueFields,
)
from .get_issue_response_fields_issuelinks_inward_issue_fields_status import (
    GetIssueResponseFieldsIssuelinksInwardIssueFieldsStatus,
)
from .get_issue_response_fields_issuelinks_outward_issue import (
    GetIssueResponseFieldsIssuelinksOutwardIssue,
)
from .get_issue_response_fields_issuelinks_outward_issue_fields import (
    GetIssueResponseFieldsIssuelinksOutwardIssueFields,
)
from .get_issue_response_fields_issuelinks_outward_issue_fields_status import (
    GetIssueResponseFieldsIssuelinksOutwardIssueFieldsStatus,
)
from .get_issue_response_fields_issuelinks_type import (
    GetIssueResponseFieldsIssuelinksType,
)
from .get_issue_response_fields_issuetype import GetIssueResponseFieldsIssuetype
from .get_issue_response_fields_parent import GetIssueResponseFieldsParent
from .get_issue_response_fields_priority import GetIssueResponseFieldsPriority
from .get_issue_response_fields_progress import GetIssueResponseFieldsProgress
from .get_issue_response_fields_project import GetIssueResponseFieldsProject
from .get_issue_response_fields_project_avatar_urls import (
    GetIssueResponseFieldsProjectAvatarUrls,
)
from .get_issue_response_fields_reporter import GetIssueResponseFieldsReporter
from .get_issue_response_fields_reporter_avatar_urls import (
    GetIssueResponseFieldsReporterAvatarUrls,
)
from .get_issue_response_fields_security import GetIssueResponseFieldsSecurity
from .get_issue_response_fields_status import GetIssueResponseFieldsStatus
from .get_issue_response_fields_status_status_category import (
    GetIssueResponseFieldsStatusStatusCategory,
)
from .get_issue_response_fields_timetracking import GetIssueResponseFieldsTimetracking
from .get_issue_response_fields_to_include import GetIssueResponseFieldsToInclude
from .get_issue_response_fields_versions_array_item_ref import (
    GetIssueResponseFieldsVersionsArrayItemRef,
)
from .get_issue_response_fields_votes import GetIssueResponseFieldsVotes
from .get_issue_response_fields_watches import GetIssueResponseFieldsWatches
from .get_issue_response_history_metadata import GetIssueResponseHistoryMetadata
from .get_issue_response_history_metadata_actor import (
    GetIssueResponseHistoryMetadataActor,
)
from .get_issue_response_history_metadata_cause import (
    GetIssueResponseHistoryMetadataCause,
)
from .get_issue_response_history_metadata_generator import (
    GetIssueResponseHistoryMetadataGenerator,
)
from .get_issue_response_operations import GetIssueResponseOperations
from .get_issue_response_operations_link_groups_array_item_ref import (
    GetIssueResponseOperationsLinkGroupsArrayItemRef,
)
from .get_issue_response_operations_link_groups_groups_array_item_ref import (
    GetIssueResponseOperationsLinkGroupsGroupsArrayItemRef,
)
from .get_issue_response_operations_link_groups_groups_header import (
    GetIssueResponseOperationsLinkGroupsGroupsHeader,
)
from .get_issue_response_operations_link_groups_groups_links_array_item_ref import (
    GetIssueResponseOperationsLinkGroupsGroupsLinksArrayItemRef,
)
from .get_issue_response_operations_link_groups_header import (
    GetIssueResponseOperationsLinkGroupsHeader,
)
from .get_issue_response_operations_link_groups_links_array_item_ref import (
    GetIssueResponseOperationsLinkGroupsLinksArrayItemRef,
)
from .get_issue_response_properties_array_item_ref import (
    GetIssueResponsePropertiesArrayItemRef,
)
from .get_issue_response_schema import GetIssueResponseSchema
from .get_issue_response_transition import GetIssueResponseTransition
from .get_issue_response_transition_error_collection import (
    GetIssueResponseTransitionErrorCollection,
)
from .get_issue_response_transition_fields import GetIssueResponseTransitionFields
from .get_issue_response_transition_fields_schema import (
    GetIssueResponseTransitionFieldsSchema,
)
from .get_issue_response_transition_to import GetIssueResponseTransitionTo
from .get_issue_response_transition_to_status_category import (
    GetIssueResponseTransitionToStatusCategory,
)
from .get_issue_response_transitions_array_item_ref import (
    GetIssueResponseTransitionsArrayItemRef,
)
from .get_issue_response_transitions_fields import GetIssueResponseTransitionsFields
from .get_issue_response_transitions_fields_schema import (
    GetIssueResponseTransitionsFieldsSchema,
)
from .get_issue_response_transitions_to import GetIssueResponseTransitionsTo
from .get_issue_response_transitions_to_status_category import (
    GetIssueResponseTransitionsToStatusCategory,
)
from .get_issue_response_update import GetIssueResponseUpdate
from .get_issue_response_update_comment import GetIssueResponseUpdateComment
from .get_issue_response_update_issuelink import GetIssueResponseUpdateIssuelink
from .get_issue_response_update_issuelink_outward_issue import (
    GetIssueResponseUpdateIssuelinkOutwardIssue,
)
from .get_issue_response_update_issuelink_type import (
    GetIssueResponseUpdateIssuelinkType,
)
from .get_issue_response_update_issuelinks import GetIssueResponseUpdateIssuelinks
from .get_issue_response_update_issuelinks_outward_issue import (
    GetIssueResponseUpdateIssuelinksOutwardIssue,
)
from .get_issue_response_update_issuelinks_type import (
    GetIssueResponseUpdateIssuelinksType,
)
from .search_issueby_jql import SearchIssuebyJQL
from .search_issueby_jql_changelog import SearchIssuebyJQLChangelog
from .search_issueby_jql_changelog_histories_array_item_ref import (
    SearchIssuebyJQLChangelogHistoriesArrayItemRef,
)
from .search_issueby_jql_changelog_histories_author import (
    SearchIssuebyJQLChangelogHistoriesAuthor,
)
from .search_issueby_jql_changelog_histories_author_avatar_urls import (
    SearchIssuebyJQLChangelogHistoriesAuthorAvatarUrls,
)
from .search_issueby_jql_changelog_histories_history_metadata import (
    SearchIssuebyJQLChangelogHistoriesHistoryMetadata,
)
from .search_issueby_jql_changelog_histories_history_metadata_actor import (
    SearchIssuebyJQLChangelogHistoriesHistoryMetadataActor,
)
from .search_issueby_jql_changelog_histories_history_metadata_cause import (
    SearchIssuebyJQLChangelogHistoriesHistoryMetadataCause,
)
from .search_issueby_jql_changelog_histories_history_metadata_generator import (
    SearchIssuebyJQLChangelogHistoriesHistoryMetadataGenerator,
)
from .search_issueby_jql_changelog_histories_items_array_item_ref import (
    SearchIssuebyJQLChangelogHistoriesItemsArrayItemRef,
)
from .search_issueby_jql_editmeta import SearchIssuebyJQLEditmeta
from .search_issueby_jql_editmeta_fields import SearchIssuebyJQLEditmetaFields
from .search_issueby_jql_editmeta_fields_schema import (
    SearchIssuebyJQLEditmetaFieldsSchema,
)
from .search_issueby_jql_fields import SearchIssuebyJQLFields
from .search_issueby_jql_fields_aggregateprogress import (
    SearchIssuebyJQLFieldsAggregateprogress,
)
from .search_issueby_jql_fields_assignee import SearchIssuebyJQLFieldsAssignee
from .search_issueby_jql_fields_assignee_avatar_urls import (
    SearchIssuebyJQLFieldsAssigneeAvatarUrls,
)
from .search_issueby_jql_fields_components_array_item_ref import (
    SearchIssuebyJQLFieldsComponentsArrayItemRef,
)
from .search_issueby_jql_fields_creator import SearchIssuebyJQLFieldsCreator
from .search_issueby_jql_fields_creator_avatar_urls import (
    SearchIssuebyJQLFieldsCreatorAvatarUrls,
)
from .search_issueby_jql_fields_fix_versions_array_item_ref import (
    SearchIssuebyJQLFieldsFixVersionsArrayItemRef,
)
from .search_issueby_jql_fields_issuetype import SearchIssuebyJQLFieldsIssuetype
from .search_issueby_jql_fields_priority import SearchIssuebyJQLFieldsPriority
from .search_issueby_jql_fields_progress import SearchIssuebyJQLFieldsProgress
from .search_issueby_jql_fields_project import SearchIssuebyJQLFieldsProject
from .search_issueby_jql_fields_project_avatar_urls import (
    SearchIssuebyJQLFieldsProjectAvatarUrls,
)
from .search_issueby_jql_fields_reporter import SearchIssuebyJQLFieldsReporter
from .search_issueby_jql_fields_reporter_avatar_urls import (
    SearchIssuebyJQLFieldsReporterAvatarUrls,
)
from .search_issueby_jql_fields_security import SearchIssuebyJQLFieldsSecurity
from .search_issueby_jql_fields_status import SearchIssuebyJQLFieldsStatus
from .search_issueby_jql_fields_status_status_category import (
    SearchIssuebyJQLFieldsStatusStatusCategory,
)
from .search_issueby_jql_fields_timetracking import SearchIssuebyJQLFieldsTimetracking
from .search_issueby_jql_fields_to_include import SearchIssuebyJQLFieldsToInclude
from .search_issueby_jql_fields_versions_array_item_ref import (
    SearchIssuebyJQLFieldsVersionsArrayItemRef,
)
from .search_issueby_jql_fields_votes import SearchIssuebyJQLFieldsVotes
from .search_issueby_jql_fields_watches import SearchIssuebyJQLFieldsWatches
from .search_issueby_jql_operations import SearchIssuebyJQLOperations
from .search_issueby_jql_operations_link_groups_array_item_ref import (
    SearchIssuebyJQLOperationsLinkGroupsArrayItemRef,
)
from .search_issueby_jql_operations_link_groups_groups_array_item_ref import (
    SearchIssuebyJQLOperationsLinkGroupsGroupsArrayItemRef,
)
from .search_issueby_jql_operations_link_groups_groups_header import (
    SearchIssuebyJQLOperationsLinkGroupsGroupsHeader,
)
from .search_issueby_jql_operations_link_groups_groups_links_array_item_ref import (
    SearchIssuebyJQLOperationsLinkGroupsGroupsLinksArrayItemRef,
)
from .search_issueby_jql_operations_link_groups_header import (
    SearchIssuebyJQLOperationsLinkGroupsHeader,
)
from .search_issueby_jql_operations_link_groups_links_array_item_ref import (
    SearchIssuebyJQLOperationsLinkGroupsLinksArrayItemRef,
)
from .search_issueby_jql_schema import SearchIssuebyJQLSchema
from .search_issueby_jql_transitions_array_item_ref import (
    SearchIssuebyJQLTransitionsArrayItemRef,
)
from .search_issueby_jql_transitions_fields import SearchIssuebyJQLTransitionsFields
from .search_issueby_jql_transitions_fields_schema import (
    SearchIssuebyJQLTransitionsFieldsSchema,
)
from .search_issueby_jql_transitions_to import SearchIssuebyJQLTransitionsTo
from .search_issueby_jql_transitions_to_status_category import (
    SearchIssuebyJQLTransitionsToStatusCategory,
)
from .transition_issue_request import TransitionIssueRequest
from .update_issue_assignee_request import UpdateIssueAssigneeRequest

__all__ = (
    "AddAttachmentBody",
    "AddAttachmentResponse",
    "AddAttachmentResponseAuthor",
    "AddAttachmentResponseAuthorAvatarUrls",
    "AddCommentRequest",
    "AddCommentResponse",
    "AddCommentResponseAuthor",
    "AddCommentResponseUpdateAuthor",
    "AddCommentResponseVisibility",
    "CreateIssueRequest",
    "CreateIssueRequestFields",
    "CreateIssueRequestFieldsIssuetype",
    "CreateIssueRequestFieldsProject",
    "CreateIssueResponse",
    "CreateIssueResponseFields",
    "CreateIssueResponseFieldsIssuetype",
    "DefaultError",
    "FindUserByEmail",
    "FindUserByEmailAccountType",
    "FindUserByEmailApplicationRoles",
    "FindUserByEmailApplicationRolesItemsArrayItemRef",
    "FindUserByEmailAvatarUrls",
    "FindUserByEmailGroups",
    "FindUserByEmailGroupsItemsArrayItemRef",
    "GetComments",
    "GetCommentsAuthor",
    "GetCommentsAuthorAvatarUrls",
    "GetCommentsPropertiesArrayItemRef",
    "GetCommentsUpdateAuthor",
    "GetCommentsUpdateAuthorAvatarUrls",
    "GetCommentsVisibility",
    "GetCommentsVisibilityVisibilityType",
    "GetInstanceInfoResponse",
    "GetIssueResponse",
    "GetIssueResponseChangelog",
    "GetIssueResponseChangelogHistoriesArrayItemRef",
    "GetIssueResponseChangelogHistoriesAuthor",
    "GetIssueResponseChangelogHistoriesAuthorAvatarUrls",
    "GetIssueResponseChangelogHistoriesHistoryMetadata",
    "GetIssueResponseChangelogHistoriesHistoryMetadataActor",
    "GetIssueResponseChangelogHistoriesHistoryMetadataCause",
    "GetIssueResponseChangelogHistoriesHistoryMetadataGenerator",
    "GetIssueResponseChangelogHistoriesItemsArrayItemRef",
    "GetIssueResponseEditmeta",
    "GetIssueResponseEditmetaFields",
    "GetIssueResponseEditmetaFieldsSchema",
    "GetIssueResponseFields",
    "GetIssueResponseFieldsAggregateprogress",
    "GetIssueResponseFieldsAssignee",
    "GetIssueResponseFieldsAssigneeAvatarUrls",
    "GetIssueResponseFieldsAttachmentArrayItemRef",
    "GetIssueResponseFieldsAttachmentAuthor",
    "GetIssueResponseFieldsAttachmentAuthorAvatarUrls",
    "GetIssueResponseFieldsComponentsArrayItemRef",
    "GetIssueResponseFieldsCreator",
    "GetIssueResponseFieldsCreatorAvatarUrls",
    "GetIssueResponseFieldsFixVersionsArrayItemRef",
    "GetIssueResponseFieldsIssuelinksArrayItemRef",
    "GetIssueResponseFieldsIssuelinksInwardIssue",
    "GetIssueResponseFieldsIssuelinksInwardIssueFields",
    "GetIssueResponseFieldsIssuelinksInwardIssueFieldsStatus",
    "GetIssueResponseFieldsIssuelinksOutwardIssue",
    "GetIssueResponseFieldsIssuelinksOutwardIssueFields",
    "GetIssueResponseFieldsIssuelinksOutwardIssueFieldsStatus",
    "GetIssueResponseFieldsIssuelinksType",
    "GetIssueResponseFieldsIssuetype",
    "GetIssueResponseFieldsParent",
    "GetIssueResponseFieldsPriority",
    "GetIssueResponseFieldsProgress",
    "GetIssueResponseFieldsProject",
    "GetIssueResponseFieldsProjectAvatarUrls",
    "GetIssueResponseFieldsReporter",
    "GetIssueResponseFieldsReporterAvatarUrls",
    "GetIssueResponseFieldsSecurity",
    "GetIssueResponseFieldsStatus",
    "GetIssueResponseFieldsStatusStatusCategory",
    "GetIssueResponseFieldsTimetracking",
    "GetIssueResponseFieldsToInclude",
    "GetIssueResponseFieldsVersionsArrayItemRef",
    "GetIssueResponseFieldsVotes",
    "GetIssueResponseFieldsWatches",
    "GetIssueResponseHistoryMetadata",
    "GetIssueResponseHistoryMetadataActor",
    "GetIssueResponseHistoryMetadataCause",
    "GetIssueResponseHistoryMetadataGenerator",
    "GetIssueResponseOperations",
    "GetIssueResponseOperationsLinkGroupsArrayItemRef",
    "GetIssueResponseOperationsLinkGroupsGroupsArrayItemRef",
    "GetIssueResponseOperationsLinkGroupsGroupsHeader",
    "GetIssueResponseOperationsLinkGroupsGroupsLinksArrayItemRef",
    "GetIssueResponseOperationsLinkGroupsHeader",
    "GetIssueResponseOperationsLinkGroupsLinksArrayItemRef",
    "GetIssueResponsePropertiesArrayItemRef",
    "GetIssueResponseSchema",
    "GetIssueResponseTransition",
    "GetIssueResponseTransitionErrorCollection",
    "GetIssueResponseTransitionFields",
    "GetIssueResponseTransitionFieldsSchema",
    "GetIssueResponseTransitionsArrayItemRef",
    "GetIssueResponseTransitionsFields",
    "GetIssueResponseTransitionsFieldsSchema",
    "GetIssueResponseTransitionsTo",
    "GetIssueResponseTransitionsToStatusCategory",
    "GetIssueResponseTransitionTo",
    "GetIssueResponseTransitionToStatusCategory",
    "GetIssueResponseUpdate",
    "GetIssueResponseUpdateComment",
    "GetIssueResponseUpdateIssuelink",
    "GetIssueResponseUpdateIssuelinkOutwardIssue",
    "GetIssueResponseUpdateIssuelinks",
    "GetIssueResponseUpdateIssuelinksOutwardIssue",
    "GetIssueResponseUpdateIssuelinksType",
    "GetIssueResponseUpdateIssuelinkType",
    "SearchIssuebyJQL",
    "SearchIssuebyJQLChangelog",
    "SearchIssuebyJQLChangelogHistoriesArrayItemRef",
    "SearchIssuebyJQLChangelogHistoriesAuthor",
    "SearchIssuebyJQLChangelogHistoriesAuthorAvatarUrls",
    "SearchIssuebyJQLChangelogHistoriesHistoryMetadata",
    "SearchIssuebyJQLChangelogHistoriesHistoryMetadataActor",
    "SearchIssuebyJQLChangelogHistoriesHistoryMetadataCause",
    "SearchIssuebyJQLChangelogHistoriesHistoryMetadataGenerator",
    "SearchIssuebyJQLChangelogHistoriesItemsArrayItemRef",
    "SearchIssuebyJQLEditmeta",
    "SearchIssuebyJQLEditmetaFields",
    "SearchIssuebyJQLEditmetaFieldsSchema",
    "SearchIssuebyJQLFields",
    "SearchIssuebyJQLFieldsAggregateprogress",
    "SearchIssuebyJQLFieldsAssignee",
    "SearchIssuebyJQLFieldsAssigneeAvatarUrls",
    "SearchIssuebyJQLFieldsComponentsArrayItemRef",
    "SearchIssuebyJQLFieldsCreator",
    "SearchIssuebyJQLFieldsCreatorAvatarUrls",
    "SearchIssuebyJQLFieldsFixVersionsArrayItemRef",
    "SearchIssuebyJQLFieldsIssuetype",
    "SearchIssuebyJQLFieldsPriority",
    "SearchIssuebyJQLFieldsProgress",
    "SearchIssuebyJQLFieldsProject",
    "SearchIssuebyJQLFieldsProjectAvatarUrls",
    "SearchIssuebyJQLFieldsReporter",
    "SearchIssuebyJQLFieldsReporterAvatarUrls",
    "SearchIssuebyJQLFieldsSecurity",
    "SearchIssuebyJQLFieldsStatus",
    "SearchIssuebyJQLFieldsStatusStatusCategory",
    "SearchIssuebyJQLFieldsTimetracking",
    "SearchIssuebyJQLFieldsToInclude",
    "SearchIssuebyJQLFieldsVersionsArrayItemRef",
    "SearchIssuebyJQLFieldsVotes",
    "SearchIssuebyJQLFieldsWatches",
    "SearchIssuebyJQLOperations",
    "SearchIssuebyJQLOperationsLinkGroupsArrayItemRef",
    "SearchIssuebyJQLOperationsLinkGroupsGroupsArrayItemRef",
    "SearchIssuebyJQLOperationsLinkGroupsGroupsHeader",
    "SearchIssuebyJQLOperationsLinkGroupsGroupsLinksArrayItemRef",
    "SearchIssuebyJQLOperationsLinkGroupsHeader",
    "SearchIssuebyJQLOperationsLinkGroupsLinksArrayItemRef",
    "SearchIssuebyJQLSchema",
    "SearchIssuebyJQLTransitionsArrayItemRef",
    "SearchIssuebyJQLTransitionsFields",
    "SearchIssuebyJQLTransitionsFieldsSchema",
    "SearchIssuebyJQLTransitionsTo",
    "SearchIssuebyJQLTransitionsToStatusCategory",
    "TransitionIssueRequest",
    "UpdateIssueAssigneeRequest",
)

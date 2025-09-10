"""Type definitions for Dooray API responses and requests."""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class DoorayApiHeader(BaseModel):
    """Common header for Dooray API responses."""
    isSuccessful: bool
    resultCode: int
    resultMessage: str


class DoorayApiResponse(BaseModel):
    """Base response model for Dooray API."""
    header: DoorayApiHeader


class DoorayErrorResponse(DoorayApiResponse):
    """Error response from Dooray API."""
    pass


class DoorayApiUnitResponse(DoorayApiResponse):
    """Response with no result data."""
    result: Optional[Dict[str, Any]] = None


# ============ Wiki Types ============

class WikiProject(BaseModel):
    """Wiki project information."""
    id: str
    code: str
    title: str
    description: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class WikiPage(BaseModel):
    """Wiki page information."""
    id: str
    title: str
    content: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    parentPageId: Optional[str] = None


class WikiListResponse(DoorayApiResponse):
    """Response for wiki list API."""
    result: List[WikiProject]
    totalCount: Optional[int] = None


class WikiPagesResponse(DoorayApiResponse):
    """Response for wiki pages list API."""
    result: List[WikiPage]
    totalCount: Optional[int] = None


class WikiPageResponse(DoorayApiResponse):
    """Response for wiki page detail API."""
    result: WikiPage


# ============ Project Types ============

class Project(BaseModel):
    """Project information."""
    id: str
    code: str
    title: str
    description: Optional[str] = None
    scope: Optional[str] = None
    state: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class ProjectPost(BaseModel):
    """Project post information."""
    id: str
    number: Optional[str] = None
    subject: str
    body: Optional[str] = None
    priority: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    dueAt: Optional[str] = None


class ProjectListResponse(DoorayApiResponse):
    """Response for project list API."""
    result: List[Project]
    totalCount: Optional[int] = None


class PostListResponse(DoorayApiResponse):
    """Response for project posts list API."""
    result: List[ProjectPost]
    totalCount: Optional[int] = None


class PostDetailResponse(DoorayApiResponse):
    """Response for project post detail API."""
    result: ProjectPost


# ============ Member Types ============

class Member(BaseModel):
    """Organization member information."""
    id: str
    organizationMemberId: str
    name: str
    emailAddress: Optional[str] = None
    userCode: Optional[str] = None


class MemberSearchResponse(DoorayApiResponse):
    """Response for member search API."""
    result: List[Member]
    totalCount: Optional[int] = None


# ============ Messenger Types ============

class Channel(BaseModel):
    """Messenger channel information."""
    id: str
    title: str
    type: str
    status: Optional[str] = None
    updatedAt: Optional[str] = None
    users: Optional[Dict[str, Any]] = None


class SimpleChannel(BaseModel):
    """Simplified channel information."""
    id: str
    title: str
    type: str
    status: Optional[str] = None
    updatedAt: Optional[str] = None
    participantCount: Optional[int] = None


class ChannelListResponse(DoorayApiResponse):
    """Response for channel list API."""
    result: List[Channel]
    totalCount: Optional[int] = None


class SimpleChannelListResponse(DoorayApiResponse):
    """Response for simplified channel list API."""
    result: List[SimpleChannel]
    totalCount: Optional[int] = None


# ============ Calendar Types ============

class Calendar(BaseModel):
    """Calendar information."""
    id: str
    title: str
    description: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class CalendarEvent(BaseModel):
    """Calendar event information."""
    id: str
    subject: str
    content: Optional[str] = None
    startedAt: str
    endedAt: str
    location: Optional[str] = None
    wholeDayFlag: Optional[bool] = False


class CalendarListResponse(DoorayApiResponse):
    """Response for calendar list API."""
    result: List[Calendar]
    totalCount: Optional[int] = None


class CalendarEventsResponse(DoorayApiResponse):
    """Response for calendar events API."""
    result: List[CalendarEvent]
    totalCount: Optional[int] = None


class CalendarEventDetailResponse(DoorayApiResponse):
    """Response for calendar event detail API."""
    result: CalendarEvent


# ============ Request Types ============

class CreateWikiPageRequest(BaseModel):
    """Request for creating wiki page."""
    title: str
    content: str
    parentPageId: Optional[str] = None


class UpdateWikiPageRequest(BaseModel):
    """Request for updating wiki page."""
    title: Optional[str] = None
    content: Optional[str] = None


class CreatePostRequest(BaseModel):
    """Request for creating project post."""
    subject: str
    body: str
    priority: Optional[str] = None
    toMemberIds: Optional[List[str]] = None
    ccMemberIds: Optional[List[str]] = None


class UpdatePostRequest(BaseModel):
    """Request for updating project post."""
    subject: Optional[str] = None
    body: Optional[str] = None
    priority: Optional[str] = None


class CreateCommentRequest(BaseModel):
    """Request for creating post comment."""
    content: str
    mimeType: Optional[str] = "text/x-markdown"


class UpdateCommentRequest(BaseModel):
    """Request for updating post comment."""
    content: str
    mimeType: Optional[str] = "text/x-markdown"


class DirectMessageRequest(BaseModel):
    """Request for sending direct message."""
    organizationMemberId: str
    text: str


class CreateChannelRequest(BaseModel):
    """Request for creating messenger channel."""
    type: str  # "private" or "direct"
    title: str
    memberIds: Optional[List[str]] = None
    capacity: Optional[str] = None


class SendChannelMessageRequest(BaseModel):
    """Request for sending channel message."""
    text: str
    organizationId: Optional[str] = None


class CreateCalendarEventRequest(BaseModel):
    """Request for creating calendar event."""
    subject: str
    content: Optional[str] = None
    startedAt: str
    endedAt: str
    location: Optional[str] = None
    wholeDayFlag: Optional[bool] = False
"""Abstract base class for Dooray API clients."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..types.dooray_api_types import DoorayApiResponse


class DoorayClient(ABC):
    """Abstract base class for Dooray API clients."""

    # ============ Wiki related methods ============
    @abstractmethod
    async def get_wikis(self, page: Optional[int] = None, size: Optional[int] = None) -> Dict[str, Any]:
        """Get list of wikis."""
        pass

    @abstractmethod
    async def get_wiki_pages(self, project_id: str, parent_page_id: Optional[str] = None) -> Dict[str, Any]:
        """Get list of wiki pages."""
        pass

    @abstractmethod
    async def get_wiki_page(self, project_id: str, page_id: str) -> Dict[str, Any]:
        """Get wiki page details."""
        pass

    @abstractmethod
    async def create_wiki_page(self, wiki_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new wiki page."""
        pass

    @abstractmethod
    async def update_wiki_page(self, wiki_id: str, page_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing wiki page."""
        pass

    # ============ Project post related methods ============

    @abstractmethod
    async def create_post(self, project_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project post."""
        pass

    @abstractmethod
    async def get_posts(
        self,
        project_id: str,
        page: Optional[int] = None,
        size: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Get list of project posts."""
        pass

    @abstractmethod
    async def get_post(self, project_id: str, post_id: str) -> Dict[str, Any]:
        """Get project post details."""
        pass

    @abstractmethod
    async def update_post(self, project_id: str, post_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing project post."""
        pass

    @abstractmethod
    async def set_post_workflow(self, project_id: str, post_id: str, workflow_id: str) -> Dict[str, Any]:
        """Set post workflow status."""
        pass

    @abstractmethod
    async def set_post_done(self, project_id: str, post_id: str) -> Dict[str, Any]:
        """Set post as done."""
        pass

    # ============ Project comment related methods ============

    @abstractmethod
    async def create_post_comment(self, project_id: str, post_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a post comment."""
        pass

    @abstractmethod
    async def get_post_comments(
        self,
        project_id: str,
        post_id: str,
        page: Optional[int] = None,
        size: Optional[int] = None,
        order: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get post comments."""
        pass

    @abstractmethod
    async def update_post_comment(
        self,
        project_id: str,
        post_id: str,
        log_id: str,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update post comment."""
        pass

    @abstractmethod
    async def delete_post_comment(self, project_id: str, post_id: str, log_id: str) -> Dict[str, Any]:
        """Delete post comment."""
        pass

    # ============ Project related methods ============

    @abstractmethod
    async def get_projects(
        self,
        page: Optional[int] = None,
        size: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Get list of projects."""
        pass

    # ============ Messenger related methods ============

    @abstractmethod
    async def search_members(
        self,
        name: Optional[str] = None,
        external_email_addresses: Optional[List[str]] = None,
        user_code: Optional[str] = None,
        id_provider_user_id: Optional[str] = None,
        page: Optional[int] = None,
        size: Optional[int] = None
    ) -> Dict[str, Any]:
        """Search organization members."""
        pass

    @abstractmethod
    async def send_direct_message(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send direct message."""
        pass

    @abstractmethod
    async def get_channels(
        self,
        page: Optional[int] = None,
        size: Optional[int] = None,
        recent_months: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get list of channels."""
        pass

    @abstractmethod
    async def get_simple_channels(
        self,
        page: Optional[int] = None,
        size: Optional[int] = None,
        recent_months: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get simplified list of channels."""
        pass

    @abstractmethod
    async def get_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get channel details."""
        pass

    @abstractmethod
    async def create_channel(self, request: Dict[str, Any], id_type: Optional[str] = None) -> Dict[str, Any]:
        """Create a new channel."""
        pass

    @abstractmethod
    async def send_channel_message(self, channel_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to channel."""
        pass

    # ============ Calendar related methods ============

    @abstractmethod
    async def get_calendars(self) -> Dict[str, Any]:
        """Get list of calendars."""
        pass

    @abstractmethod
    async def get_calendar_detail(self, calendar_id: str) -> Dict[str, Any]:
        """Get calendar details."""
        pass

    @abstractmethod
    async def get_calendar_events(
        self,
        calendars: Optional[str],
        time_min: str,
        time_max: str,
        post_type: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get calendar events."""
        pass

    @abstractmethod
    async def get_calendar_event_detail(self, calendar_id: str, event_id: str) -> Dict[str, Any]:
        """Get calendar event details."""
        pass

    @abstractmethod
    async def create_calendar_event(self, calendar_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create calendar event."""
        pass

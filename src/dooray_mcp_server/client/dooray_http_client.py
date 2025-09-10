"""HTTP client implementation for Dooray API."""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
import structlog

from .dooray_client import DoorayClient


logger = structlog.get_logger(__name__)


class DoorayHttpClient(DoorayClient):
    """HTTP client implementation for Dooray API."""

    def __init__(self, base_url: str, dooray_api_key: str):
        self.base_url = base_url.rstrip("/")
        self.dooray_api_key = dooray_api_key

        # Configure HTTP logging level (for future use)
        _ = os.getenv("DOORAY_HTTP_LOG_LEVEL", "WARN").upper()
        # Setup HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"dooray-api {self.dooray_api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )

        logger.info("Dooray HTTP client initialized", base_url=self.base_url)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def _execute_api_call(
        self,
        method: str,
        endpoint: str,
        operation: str,
        expected_status: int = 200,
        success_message: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute API call with common error handling."""
        try:
            logger.info("API request", operation=operation, endpoint=endpoint)

            response = await self.client.request(method, endpoint, **kwargs)

            logger.info("API response received",
                       status=response.status_code,
                       operation=operation)

            if response.status_code == expected_status:
                result = response.json()
                if success_message:
                    logger.info(success_message)
                return result
            else:
                return await self._handle_error_response(response)

        except httpx.RequestError as e:
            error_msg = f"Network error during API call: {str(e)}"
            logger.error(error_msg, operation=operation)
            raise Exception(error_msg) from e
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON response: {str(e)}"
            logger.error(error_msg, operation=operation)
            raise Exception(error_msg) from e

    async def _handle_error_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle error responses from Dooray API."""
        try:
            error_data = response.json()
            logger.error("API error response",
                        status_code=response.status_code,
                        error_data=error_data)

            # Return error response in expected format
            if "header" in error_data:
                return error_data
            else:
                # Create standard error response format
                return {
                    "header": {
                        "isSuccessful": False,
                        "resultCode": response.status_code,
                        "resultMessage": str(error_data)
                    }
                }
        except json.JSONDecodeError:
            error_text = response.text
            logger.error("Failed to parse error response",
                        status_code=response.status_code,
                        response_text=error_text)
            return {
                "header": {
                    "isSuccessful": False,
                    "resultCode": response.status_code,
                    "resultMessage": f"API call failed with status {response.status_code}: {error_text}"
                }
            }

    # ============ Wiki related methods ============

    async def get_wikis(self, page: Optional[int] = None, size: Optional[int] = None) -> Dict[str, Any]:
        """Get list of wikis."""
        params = {}
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size

        return await self._execute_api_call(
            "GET", "/wiki/v1/wikis",
            operation="GET /wiki/v1/wikis",
            success_message="Wiki list retrieved successfully",
            params=params
        )

    async def get_wiki_pages(self, project_id: str, parent_page_id: Optional[str] = None) -> Dict[str, Any]:
        """Get list of wiki pages."""
        params = {}
        if parent_page_id:
            params["parentPageId"] = parent_page_id

        return await self._execute_api_call(
            "GET", f"/wiki/v1/wikis/{project_id}/pages",
            operation=f"GET /wiki/v1/wikis/{project_id}/pages",
            success_message="Wiki pages list retrieved successfully",
            params=params
        )

    async def get_wiki_page(self, project_id: str, page_id: str) -> Dict[str, Any]:
        """Get wiki page details."""
        return await self._execute_api_call(
            "GET", f"/wiki/v1/wikis/{project_id}/pages/{page_id}",
            operation=f"GET /wiki/v1/wikis/{project_id}/pages/{page_id}",
            success_message="Wiki page details retrieved successfully"
        )

    async def create_wiki_page(self, wiki_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new wiki page."""
        return await self._execute_api_call(
            "POST", f"/wiki/v1/wikis/{wiki_id}/pages",
            operation=f"POST /wiki/v1/wikis/{wiki_id}/pages",
            expected_status=201,
            success_message="Wiki page created successfully",
            json=request
        )

    async def update_wiki_page(self, wiki_id: str, page_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing wiki page."""
        return await self._execute_api_call(
            "PUT", f"/wiki/v1/wikis/{wiki_id}/pages/{page_id}",
            operation=f"PUT /wiki/v1/wikis/{wiki_id}/pages/{page_id}",
            success_message="Wiki page updated successfully",
            json=request
        )

    # ============ Project post related methods ============

    async def create_post(self, project_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project post."""
        return await self._execute_api_call(
            "POST", f"/project/v1/projects/{project_id}/posts",
            operation=f"POST /project/v1/projects/{project_id}/posts",
            success_message="Project post created successfully",
            json=request
        )

    async def get_posts(
        self,
        project_id: str,
        page: Optional[int] = None,
        size: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Get list of project posts."""
        params = {}
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size

        # Add additional filter parameters
        for key, value in kwargs.items():
            if value is not None:
                if isinstance(value, list) and len(value) > 0:
                    params[key] = ",".join(str(v) for v in value)
                elif not isinstance(value, list):
                    params[key] = value

        return await self._execute_api_call(
            "GET", f"/project/v1/projects/{project_id}/posts",
            operation=f"GET /project/v1/projects/{project_id}/posts",
            success_message="Project posts list retrieved successfully",
            params=params
        )

    async def get_post(self, project_id: str, post_id: str) -> Dict[str, Any]:
        """Get project post details."""
        return await self._execute_api_call(
            "GET", f"/project/v1/projects/{project_id}/posts/{post_id}",
            operation=f"GET /project/v1/projects/{project_id}/posts/{post_id}",
            success_message="Project post details retrieved successfully"
        )

    async def update_post(self, project_id: str, post_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing project post."""
        return await self._execute_api_call(
            "PUT", f"/project/v1/projects/{project_id}/posts/{post_id}",
            operation=f"PUT /project/v1/projects/{project_id}/posts/{post_id}",
            success_message="Project post updated successfully",
            json=request
        )

    async def set_post_workflow(self, project_id: str, post_id: str, workflow_id: str) -> Dict[str, Any]:
        """Set post workflow status."""
        request = {"workflowId": workflow_id}
        return await self._execute_api_call(
            "POST", f"/project/v1/projects/{project_id}/posts/{post_id}/set-workflow",
            operation=f"POST /project/v1/projects/{project_id}/posts/{post_id}/set-workflow",
            success_message="Post workflow status updated successfully",
            json=request
        )

    async def set_post_done(self, project_id: str, post_id: str) -> Dict[str, Any]:
        """Set post as done."""
        return await self._execute_api_call(
            "POST", f"/project/v1/projects/{project_id}/posts/{post_id}/set-done",
            operation=f"POST /project/v1/projects/{project_id}/posts/{post_id}/set-done",
            success_message="Post marked as done successfully"
        )

    # ============ Project comment related methods ============

    async def create_post_comment(self, project_id: str, post_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a post comment."""
        return await self._execute_api_call(
            "POST", f"/project/v1/projects/{project_id}/posts/{post_id}/logs",
            operation=f"POST /project/v1/projects/{project_id}/posts/{post_id}/logs",
            success_message="Post comment created successfully",
            json=request
        )

    async def get_post_comments(
        self,
        project_id: str,
        post_id: str,
        page: Optional[int] = None,
        size: Optional[int] = None,
        order: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get post comments."""
        params = {}
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size
        if order is not None:
            params["order"] = order

        return await self._execute_api_call(
            "GET", f"/project/v1/projects/{project_id}/posts/{post_id}/logs",
            operation=f"GET /project/v1/projects/{project_id}/posts/{post_id}/logs",
            success_message="Post comments retrieved successfully",
            params=params
        )

    async def update_post_comment(
        self,
        project_id: str,
        post_id: str,
        log_id: str,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update post comment."""
        return await self._execute_api_call(
            "PUT", f"/project/v1/projects/{project_id}/posts/{post_id}/logs/{log_id}",
            operation=f"PUT /project/v1/projects/{project_id}/posts/{post_id}/logs/{log_id}",
            success_message="Post comment updated successfully",
            json=request
        )

    async def delete_post_comment(self, project_id: str, post_id: str, log_id: str) -> Dict[str, Any]:
        """Delete post comment."""
        return await self._execute_api_call(
            "DELETE", f"/project/v1/projects/{project_id}/posts/{post_id}/logs/{log_id}",
            operation=f"DELETE /project/v1/projects/{project_id}/posts/{post_id}/logs/{log_id}",
            success_message="Post comment deleted successfully"
        )

    # ============ Project related methods ============

    async def get_projects(
        self,
        page: Optional[int] = None,
        size: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Get list of projects."""
        params = {"member": "me"}  # Only get projects for current user
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size

        # Add additional filter parameters
        for key, value in kwargs.items():
            if value is not None:
                params[key] = value

        return await self._execute_api_call(
            "GET", "/project/v1/projects",
            operation="GET /project/v1/projects",
            success_message="Projects list retrieved successfully",
            params=params
        )

    # ============ Messenger related methods ============

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
        params = {}
        if name is not None:
            params["name"] = name
        if external_email_addresses is not None:
            params["externalEmailAddresses"] = ",".join(external_email_addresses)
        if user_code is not None:
            params["userCode"] = user_code
        if id_provider_user_id is not None:
            params["idProviderUserId"] = id_provider_user_id
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size

        return await self._execute_api_call(
            "GET", "/common/v1/members",
            operation="GET /common/v1/members",
            success_message="Members search completed successfully",
            params=params
        )

    async def send_direct_message(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send direct message."""
        return await self._execute_api_call(
            "POST", "/messenger/v1/channels/direct-send",
            operation="POST /messenger/v1/channels/direct-send",
            success_message="Direct message sent successfully",
            json=request
        )

    async def get_channels(
        self,
        page: Optional[int] = None,
        size: Optional[int] = None,
        recent_months: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get list of channels."""
        params = {}
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size

        response = await self._execute_api_call(
            "GET", "/messenger/v1/channels",
            operation="GET /messenger/v1/channels",
            success_message="Channels list retrieved successfully",
            params=params
        )

        # Apply client-side filtering for recent_months if specified
        if recent_months and recent_months > 0 and response.get("header", {}).get("isSuccessful"):
            cutoff_date = datetime.now() - timedelta(days=recent_months * 30)
            filtered_channels = []

            for channel in response.get("result", []):
                updated_at_str = channel.get("updatedAt")
                if updated_at_str:
                    try:
                        # Parse the date string (handle timezone info)
                        updated_at_str = updated_at_str.replace("+09:00", "").split(".")[0]
                        updated_at = datetime.fromisoformat(updated_at_str)
                        if updated_at > cutoff_date:
                            filtered_channels.append(channel)
                    except Exception as e:
                        logger.warning("Date parsing failed",
                                     channel_id=channel.get("id"),
                                     updated_at=updated_at_str,
                                     error=str(e))

            logger.info("Filtered channels by recent months",
                       original_count=len(response.get("result", [])),
                       filtered_count=len(filtered_channels),
                       recent_months=recent_months)

            response["result"] = filtered_channels
            response["totalCount"] = len(filtered_channels)

        return response

    async def get_simple_channels(
        self,
        page: Optional[int] = None,
        size: Optional[int] = None,
        recent_months: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get simplified list of channels."""
        # Reuse get_channels and simplify the response
        response = await self.get_channels(page, size, recent_months)

        if response.get("header", {}).get("isSuccessful"):
            simple_channels = []
            for channel in response.get("result", []):
                simple_channel = {
                    "id": channel.get("id"),
                    "title": channel.get("title"),
                    "type": channel.get("type"),
                    "status": channel.get("status"),
                    "updatedAt": channel.get("updatedAt"),
                    "participantCount": len(channel.get("users", {}).get("participants", []))
                }
                simple_channels.append(simple_channel)

            response["result"] = simple_channels
            logger.info("Simplified channel information",
                       channel_count=len(simple_channels))

        return response

    async def get_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get channel details."""
        try:
            # Get all channels and find the specific one
            response = await self.get_channels()
            if response.get("header", {}).get("isSuccessful"):
                for channel in response.get("result", []):
                    if channel.get("id") == channel_id:
                        logger.info("Channel details retrieved", channel_id=channel_id)
                        return channel

                logger.warning("Channel not found", channel_id=channel_id)
                return None
            else:
                logger.error("Failed to retrieve channels list",
                           error=response.get("header", {}).get("resultMessage"))
                return None
        except Exception as e:
            logger.error("Error retrieving channel details",
                        channel_id=channel_id, error=str(e))
            return None

    async def create_channel(self, request: Dict[str, Any], id_type: Optional[str] = None) -> Dict[str, Any]:
        """Create a new channel."""
        params = {}
        if id_type is not None:
            params["idType"] = id_type

        return await self._execute_api_call(
            "POST", "/messenger/v1/channels",
            operation="POST /messenger/v1/channels",
            success_message="Channel created successfully",
            json=request,
            params=params
        )

    async def send_channel_message(self, channel_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to channel."""
        return await self._execute_api_call(
            "POST", f"/messenger/v1/channels/{channel_id}/logs",
            operation=f"POST /messenger/v1/channels/{channel_id}/logs",
            success_message="Channel message sent successfully",
            json=request
        )

    # ============ Calendar related methods ============

    async def get_calendars(self) -> Dict[str, Any]:
        """Get list of calendars."""
        return await self._execute_api_call(
            "GET", "/calendar/v1/calendars",
            operation="GET /calendar/v1/calendars",
            success_message="Calendars list retrieved successfully"
        )

    async def get_calendar_detail(self, calendar_id: str) -> Dict[str, Any]:
        """Get calendar details."""
        return await self._execute_api_call(
            "GET", f"/calendar/v1/calendars/{calendar_id}",
            operation=f"GET /calendar/v1/calendars/{calendar_id}",
            success_message="Calendar details retrieved successfully"
        )

    async def get_calendar_events(
        self,
        calendars: Optional[str],
        time_min: str,
        time_max: str,
        post_type: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get calendar events."""
        params = {
            "timeMin": time_min,
            "timeMax": time_max
        }
        if calendars is not None:
            params["calendars"] = calendars
        if post_type is not None:
            params["postType"] = post_type
        if category is not None:
            params["category"] = category

        return await self._execute_api_call(
            "GET", "/calendar/v1/calendars/*/events",
            operation="GET /calendar/v1/calendars/*/events",
            success_message="Calendar events retrieved successfully",
            params=params
        )

    async def get_calendar_event_detail(self, calendar_id: str, event_id: str) -> Dict[str, Any]:
        """Get calendar event details."""
        return await self._execute_api_call(
            "GET", f"/calendar/v1/calendars/{calendar_id}/events/{event_id}",
            operation=f"GET /calendar/v1/calendars/{calendar_id}/events/{event_id}",
            success_message="Calendar event details retrieved successfully"
        )

    async def create_calendar_event(self, calendar_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create calendar event."""
        return await self._execute_api_call(
            "POST", f"/calendar/v1/calendars/{calendar_id}/events",
            operation=f"POST /calendar/v1/calendars/{calendar_id}/events",
            success_message="Calendar event created successfully",
            json=request
        )

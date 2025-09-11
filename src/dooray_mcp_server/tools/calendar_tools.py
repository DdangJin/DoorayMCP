"""Calendar-related MCP tools."""

import json
from typing import Any, Dict, List, Optional, Sequence

from mcp.types import Tool
import structlog

from ..client.dooray_client import DoorayClient

logger = structlog.get_logger(__name__)


def get_calendars_tool() -> Tool:
    """Tool for getting calendars list."""
    return Tool(
        name="dooray_calendar_list",
        description="두레이에서 접근 가능한 캘린더 목록을 조회합니다. 캘린더 ID를 확인하거나 사용 가능한 캘린더를 확인할 때 사용합니다.",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    )


async def get_calendars_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for getting calendars list."""
    try:
        response = await dooray_client.get_calendars()

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "calendars": response.get("result", []),
                "totalCount": len(response.get("result", [])),
                "message": "캘린더 목록을 성공적으로 조회했습니다."
            }
            logger.info("Calendars retrieved successfully",
                       count=len(response.get("result", [])))
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": "캘린더 목록 조회에 실패했습니다."
            }
            logger.error("Failed to retrieve calendars", error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "캘린더 목록 조회 중 오류가 발생했습니다."
        }
        logger.error("Exception in get_calendars_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def get_calendar_detail_tool() -> Tool:
    """Tool for getting calendar details."""
    return Tool(
        name="dooray_calendar_detail",
        description="특정 캘린더의 상세 정보를 조회합니다. 캘린더 멤버 목록, 권한 정보(소유자, 위임자, 편집자 등), 위임 정보를 확인할 수 있습니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "calendar_id": {
                    "type": "string",
                    "description": "조회할 캘린더 ID"
                }
            },
            "required": ["calendar_id"]
        }
    )


async def get_calendar_detail_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for getting calendar details."""
    try:
        calendar_id = arguments["calendar_id"]

        response = await dooray_client.get_calendar_detail(calendar_id)

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "calendar": response.get("result"),
                "message": f"캘린더 상세 정보를 성공적으로 조회했습니다. (캘린더: {calendar_id})"
            }
            logger.info("Calendar details retrieved successfully",
                       calendar_id=calendar_id)
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"캘린더 상세 정보 조회에 실패했습니다. (캘린더: {calendar_id})"
            }
            logger.error("Failed to retrieve calendar details",
                        calendar_id=calendar_id,
                        error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "캘린더 상세 정보 조회 중 오류가 발생했습니다."
        }
        logger.error("Exception in get_calendar_detail_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def get_calendar_events_tool() -> Tool:
    """Tool for getting calendar events."""
    return Tool(
        name="dooray_calendar_events",
        description="지정된 기간의 캘린더 이벤트(일정) 목록을 조회합니다. 특정 날짜나 기간의 일정을 확인할 때 사용합니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "time_min": {
                    "type": "string",
                    "description": "조회 시작 시간 (ISO 8601 형식, 예: 2025-04-11T00:00:00+09:00)"
                },
                "time_max": {
                    "type": "string",
                    "description": "조회 종료 시간 (ISO 8601 형식, 예: 2025-04-12T00:00:00+09:00)"
                },
                "calendars": {
                    "type": "string",
                    "description": "조회할 캘린더 ID 목록 (쉼표로 구분, 선택사항)"
                },
                "post_type": {
                    "type": "string",
                    "enum": ["toMe", "toCcMe", "fromToCcMe"],
                    "description": "참가자 필터: toMe(나에게), toCcMe(나에게+참조), fromToCcMe(모든 관련) (선택사항)"
                },
                "category": {
                    "type": "string",
                    "enum": ["general", "post", "milestone"],
                    "description": "카테고리 필터: general(일반 일정), post(업무), milestone(마일스톤) (선택사항)"
                }
            },
            "required": ["time_min", "time_max"]
        }
    )


async def get_calendar_events_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for getting calendar events."""
    try:
        time_min = arguments["time_min"]
        time_max = arguments["time_max"]
        calendars = arguments.get("calendars")
        post_type = arguments.get("post_type")
        category = arguments.get("category")

        response = await dooray_client.get_calendar_events(
            calendars=calendars,
            time_min=time_min,
            time_max=time_max,
            post_type=post_type,
            category=category
        )

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "events": response.get("result", []),
                "totalCount": len(response.get("result", [])),
                "message": f"캘린더 이벤트 목록을 성공적으로 조회했습니다. ({time_min} ~ {time_max})"
            }
            logger.info("Calendar events retrieved successfully",
                       time_min=time_min,
                       time_max=time_max,
                       count=len(response.get("result", [])))
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"캘린더 이벤트 목록 조회에 실패했습니다. ({time_min} ~ {time_max})"
            }
            logger.error("Failed to retrieve calendar events",
                        time_min=time_min,
                        time_max=time_max,
                        error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "캘린더 이벤트 목록 조회 중 오류가 발생했습니다."
        }
        logger.error("Exception in get_calendar_events_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def get_calendar_event_detail_tool() -> Tool:
    """Tool for getting calendar event details."""
    return Tool(
        name="dooray_calendar_event_detail",
        description="특정 캘린더 이벤트(일정)의 상세 정보를 조회합니다. 주최자, 참가자, 참조자의 상세 정보와 참가 상황을 확인할 수 있습니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "calendar_id": {
                    "type": "string",
                    "description": "캘린더 ID"
                },
                "event_id": {
                    "type": "string",
                    "description": "이벤트 ID"
                }
            },
            "required": ["calendar_id", "event_id"]
        }
    )


async def get_calendar_event_detail_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for getting calendar event details."""
    try:
        calendar_id = arguments["calendar_id"]
        event_id = arguments["event_id"]

        response = await dooray_client.get_calendar_event_detail(calendar_id, event_id)

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "event": response.get("result"),
                "message": f"캘린더 이벤트 상세 정보를 성공적으로 조회했습니다. (이벤트: {event_id})"
            }
            logger.info("Calendar event details retrieved successfully",
                       calendar_id=calendar_id,
                       event_id=event_id)
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"캘린더 이벤트 상세 정보 조회에 실패했습니다. (이벤트: {event_id})"
            }
            logger.error("Failed to retrieve calendar event details",
                        calendar_id=calendar_id,
                        event_id=event_id,
                        error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "캘린더 이벤트 상세 정보 조회 중 오류가 발생했습니다."
        }
        logger.error("Exception in get_calendar_event_detail_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def create_calendar_event_tool() -> Tool:
    """Tool for creating calendar event."""
    return Tool(
        name="dooray_calendar_create_event",
        description="새로운 캘린더 이벤트(일정)를 생성합니다. 회의, 약속 등의 일정을 등록할 때 사용합니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "calendar_id": {
                    "type": "string",
                    "description": "이벤트를 생성할 캘린더 ID"
                },
                "subject": {
                    "type": "string",
                    "description": "이벤트 제목"
                },
                "content": {
                    "type": "string",
                    "description": "이벤트 내용 (선택사항)"
                },
                "started_at": {
                    "type": "string",
                    "description": "시작 시간 (ISO 8601 형식, 예: 2025-04-11T14:00:00+09:00)"
                },
                "ended_at": {
                    "type": "string",
                    "description": "종료 시간 (ISO 8601 형식, 예: 2025-04-11T15:00:00+09:00)"
                },
                "location": {
                    "type": "string",
                    "description": "장소 (선택사항)"
                },
                "whole_day_flag": {
                    "type": "boolean",
                    "description": "종일 이벤트 여부 (기본값: false)",
                    "default": False
                }
            },
            "required": ["calendar_id", "subject", "started_at", "ended_at"]
        }
    )


async def create_calendar_event_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for creating calendar event."""
    try:
        calendar_id = arguments["calendar_id"]
        request_data = {
            "subject": arguments["subject"],
            "startedAt": arguments["started_at"],
            "endedAt": arguments["ended_at"],
            "wholeDayFlag": arguments.get("whole_day_flag", False)
        }

        if "content" in arguments:
            request_data["content"] = arguments["content"]
        if "location" in arguments:
            request_data["location"] = arguments["location"]

        response = await dooray_client.create_calendar_event(calendar_id, request_data)

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "event": response.get("result"),
                "message": f"캘린더 이벤트를 성공적으로 생성했습니다. (제목: {arguments['subject']})"
            }
            logger.info("Calendar event created successfully",
                       calendar_id=calendar_id,
                       subject=arguments["subject"])
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"캘린더 이벤트 생성에 실패했습니다. (제목: {arguments['subject']})"
            }
            logger.error("Failed to create calendar event",
                        calendar_id=calendar_id,
                        subject=arguments["subject"],
                        error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "캘린더 이벤트 생성 중 오류가 발생했습니다."
        }
        logger.error("Exception in create_calendar_event_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]

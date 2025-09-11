"""Messenger-related MCP tools."""

import json
from typing import Any, Dict, List, Optional, Sequence

from mcp.types import Tool
import structlog

from ..client.dooray_client import DoorayClient

logger = structlog.get_logger(__name__)


def search_members_tool() -> Tool:
    """Tool for searching organization members."""
    return Tool(
        name="dooray_messenger_search_members",
        description="두레이 조직의 멤버를 검색합니다. 이름, 이메일, 사용자 코드 등으로 검색할 수 있습니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "검색할 멤버 이름"
                },
                "external_email_addresses": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "검색할 이메일 주소 목록"
                },
                "user_code": {
                    "type": "string",
                    "description": "검색할 사용자 코드"
                },
                "page": {
                    "type": "integer",
                    "description": "조회할 페이지 번호 (0부터 시작, 기본값: 0)",
                    "default": 0
                },
                "size": {
                    "type": "integer",
                    "description": "한 페이지당 결과 수 (기본값: 10)",
                    "default": 10
                }
            }
        }
    )


async def search_members_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for searching members."""
    try:
        name = arguments.get("name")
        external_email_addresses = arguments.get("external_email_addresses")
        user_code = arguments.get("user_code")
        page = arguments.get("page", 0)
        size = arguments.get("size", 10)

        response = await dooray_client.search_members(
            name=name,
            external_email_addresses=external_email_addresses,
            user_code=user_code,
            page=page,
            size=size
        )

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "members": response.get("result", []),
                "totalCount": response.get("totalCount"),
                "message": "멤버 검색을 성공적으로 완료했습니다."
            }
            logger.info("Members search completed successfully",
                       count=len(response.get("result", [])))
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": "멤버 검색에 실패했습니다."
            }
            logger.error("Failed to search members", error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "멤버 검색 중 오류가 발생했습니다."
        }
        logger.error("Exception in search_members_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def send_direct_message_tool() -> Tool:
    """Tool for sending direct message."""
    return Tool(
        name="dooray_messenger_send_direct_message",
        description="특정 멤버에게 1:1 다이렉트 메시지를 전송합니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "organization_member_id": {
                    "type": "string",
                    "description": "수신자 조직 멤버 ID"
                },
                "text": {
                    "type": "string",
                    "description": "전송할 메시지 내용"
                }
            },
            "required": ["organization_member_id", "text"]
        }
    )


async def send_direct_message_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for sending direct message."""
    try:
        request_data = {
            "organizationMemberId": arguments["organization_member_id"],
            "text": arguments["text"]
        }

        response = await dooray_client.send_direct_message(request_data)

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "message": f"다이렉트 메시지를 성공적으로 전송했습니다. (수신자: {arguments['organization_member_id']})"
            }
            logger.info("Direct message sent successfully",
                       recipient=arguments["organization_member_id"])
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"다이렉트 메시지 전송에 실패했습니다. (수신자: {arguments['organization_member_id']})"
            }
            logger.error("Failed to send direct message",
                        recipient=arguments["organization_member_id"],
                        error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "다이렉트 메시지 전송 중 오류가 발생했습니다."
        }
        logger.error("Exception in send_direct_message_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def get_channels_tool() -> Tool:
    """Tool for getting channels list."""
    return Tool(
        name="dooray_messenger_get_channels",
        description="접근 가능한 메신저 채널 목록을 조회합니다. 최근 N개월 이내에 업데이트된 채널만 필터링할 수 있습니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "page": {
                    "type": "integer",
                    "description": "조회할 페이지 번호 (0부터 시작, 기본값: 0)",
                    "default": 0
                },
                "size": {
                    "type": "integer",
                    "description": "한 페이지당 결과 수 (기본값: 200)",
                    "default": 200
                },
                "recent_months": {
                    "type": "integer",
                    "description": "최근 N개월 이내 업데이트된 채널만 조회 (선택사항)"
                }
            }
        }
    )


async def get_channels_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for getting channels list."""
    try:
        page = arguments.get("page", 0)
        size = arguments.get("size", 200)
        recent_months = arguments.get("recent_months")

        response = await dooray_client.get_channels(page, size, recent_months)

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "channels": response.get("result", []),
                "totalCount": response.get("totalCount"),
                "message": "채널 목록을 성공적으로 조회했습니다."
            }
            if recent_months:
                result["message"] += f" (최근 {recent_months}개월 필터링 적용)"

            logger.info("Channels retrieved successfully",
                       count=len(response.get("result", [])),
                       recent_months=recent_months)
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": "채널 목록 조회에 실패했습니다."
            }
            logger.error("Failed to retrieve channels", error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "채널 목록 조회 중 오류가 발생했습니다."
        }
        logger.error("Exception in get_channels_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def get_simple_channels_tool() -> Tool:
    """Tool for getting simplified channels list."""
    return Tool(
        name="dooray_messenger_get_simple_channels",
        description="간소화된 채널 목록을 조회합니다. ID, 제목, 타입, 상태, 업데이트 시간, 참가자 수만 포함됩니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "page": {
                    "type": "integer",
                    "description": "조회할 페이지 번호 (0부터 시작, 기본값: 0)",
                    "default": 0
                },
                "size": {
                    "type": "integer",
                    "description": "한 페이지당 결과 수 (기본값: 50)",
                    "default": 50
                },
                "recent_months": {
                    "type": "integer",
                    "description": "최근 N개월 이내 업데이트된 채널만 조회 (선택사항)"
                }
            }
        }
    )


async def get_simple_channels_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for getting simplified channels list."""
    try:
        page = arguments.get("page", 0)
        size = arguments.get("size", 50)
        recent_months = arguments.get("recent_months")

        response = await dooray_client.get_simple_channels(page, size, recent_months)

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "channels": response.get("result", []),
                "totalCount": response.get("totalCount"),
                "message": "간소화된 채널 목록을 성공적으로 조회했습니다."
            }
            if recent_months:
                result["message"] += f" (최근 {recent_months}개월 필터링 적용)"

            logger.info("Simple channels retrieved successfully",
                       count=len(response.get("result", [])),
                       recent_months=recent_months)
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": "간소화된 채널 목록 조회에 실패했습니다."
            }
            logger.error("Failed to retrieve simple channels", error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "간소화된 채널 목록 조회 중 오류가 발생했습니다."
        }
        logger.error("Exception in get_simple_channels_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def get_channel_tool() -> Tool:
    """Tool for getting channel details."""
    return Tool(
        name="dooray_messenger_get_channel",
        description="특정 채널의 상세 정보를 조회합니다. 채널의 모든 멤버, 설정 등의 상세 정보를 확인할 수 있습니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "channel_id": {
                    "type": "string",
                    "description": "조회할 채널 ID"
                }
            },
            "required": ["channel_id"]
        }
    )


async def get_channel_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for getting channel details."""
    try:
        channel_id = arguments["channel_id"]

        channel = await dooray_client.get_channel(channel_id)

        if channel:
            result = {
                "success": True,
                "channel": channel,
                "message": f"채널 상세 정보를 성공적으로 조회했습니다. (채널: {channel_id})"
            }
            logger.info("Channel details retrieved successfully",
                       channel_id=channel_id)
        else:
            result = {
                "success": False,
                "error": "Channel not found",
                "message": f"채널을 찾을 수 없습니다. (채널: {channel_id})"
            }
            logger.warning("Channel not found", channel_id=channel_id)

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "채널 상세 정보 조회 중 오류가 발생했습니다."
        }
        logger.error("Exception in get_channel_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def create_channel_tool() -> Tool:
    """Tool for creating channel."""
    return Tool(
        name="dooray_messenger_create_channel",
        description="새로운 메신저 채널을 생성합니다. private 또는 direct 타입을 지원합니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["private", "direct"],
                    "description": "채널 타입 (private 또는 direct)"
                },
                "title": {
                    "type": "string",
                    "description": "채널 제목"
                },
                "member_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "초대할 멤버 ID 목록"
                },
                "capacity": {
                    "type": "string",
                    "description": "채널 최대 인원 (선택사항)"
                },
                "id_type": {
                    "type": "string",
                    "enum": ["email", "memberId"],
                    "description": "멤버 ID 타입 (email 또는 memberId, 선택사항)"
                }
            },
            "required": ["type", "title", "member_ids"]
        }
    )


async def create_channel_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for creating channel."""
    try:
        request_data = {
            "type": arguments["type"],
            "title": arguments["title"],
            "memberIds": arguments["member_ids"]
        }

        if "capacity" in arguments:
            request_data["capacity"] = arguments["capacity"]

        id_type = arguments.get("id_type")

        response = await dooray_client.create_channel(request_data, id_type)

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "channel": response.get("result"),
                "message": f"채널을 성공적으로 생성했습니다. (제목: {arguments['title']})"
            }
            logger.info("Channel created successfully",
                       title=arguments["title"],
                       channel_type=arguments["type"])
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"채널 생성에 실패했습니다. (제목: {arguments['title']})"
            }
            logger.error("Failed to create channel",
                        title=arguments["title"],
                        error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "채널 생성 중 오류가 발생했습니다."
        }
        logger.error("Exception in create_channel_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def send_channel_message_tool() -> Tool:
    """Tool for sending channel message."""
    return Tool(
        name="dooray_messenger_send_channel_message",
        description="메신저 채널에 메시지를 전송합니다. 멘션 기능을 지원합니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "channel_id": {
                    "type": "string",
                    "description": "메시지를 전송할 채널 ID"
                },
                "text": {
                    "type": "string",
                    "description": "전송할 메시지 내용"
                },
                "mention_members": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "멤버 ID"},
                            "name": {"type": "string", "description": "멤버 이름"},
                            "organizationId": {"type": "string", "description": "조직 ID"}
                        },
                        "required": ["id", "name", "organizationId"]
                    },
                    "description": "멘션할 멤버 목록 (선택사항)"
                },
                "mention_all": {
                    "type": "boolean",
                    "description": "전체 멘션 여부 (@Channel, 선택사항)",
                    "default": False
                }
            },
            "required": ["channel_id", "text"]
        }
    )


async def send_channel_message_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for sending channel message."""
    try:
        channel_id = arguments["channel_id"]
        text = arguments["text"]
        mention_members = arguments.get("mention_members", [])
        mention_all = arguments.get("mention_all", False)

        # Build message text with mentions
        message_text = text

        # Add individual member mentions
        for member in mention_members:
            member_mention = f"[@{member['name']}](dooray://{member['organizationId']}/members/{member['id']} \"member\")"
            if member_mention not in message_text:
                message_text = member_mention + "\n" + message_text

        # Add channel mention if requested
        if mention_all:
            # Note: This would need the channel's organizationId - simplified for this example
            channel_mention = "[@Channel](dooray://organization/channels/" + channel_id + " \"channel\")"
            if channel_mention not in message_text:
                message_text = channel_mention + "\n" + message_text

        request_data = {
            "text": message_text
        }

        response = await dooray_client.send_channel_message(channel_id, request_data)

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "message": f"채널 메시지를 성공적으로 전송했습니다. (채널: {channel_id})"
            }
            logger.info("Channel message sent successfully",
                       channel_id=channel_id,
                       mention_count=len(mention_members),
                       mention_all=mention_all)
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"채널 메시지 전송에 실패했습니다. (채널: {channel_id})"
            }
            logger.error("Failed to send channel message",
                        channel_id=channel_id,
                        error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "채널 메시지 전송 중 오류가 발생했습니다."
        }
        logger.error("Exception in send_channel_message_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]

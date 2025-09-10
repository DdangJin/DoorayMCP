"""Project-related MCP tools."""

import json
from typing import Any, Dict, List, Optional, Sequence

from mcp.types import Tool
import structlog

from ..client.dooray_client import DoorayClient

logger = structlog.get_logger(__name__)


def get_projects_tool() -> Tool:
    """Tool for getting list of projects."""
    return Tool(
        name="dooray_project_list_projects",
        description="접근 가능한 프로젝트 목록을 조회합니다.",
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
                "type": {
                    "type": "string",
                    "description": "프로젝트 타입 필터 (선택사항)"
                },
                "scope": {
                    "type": "string",
                    "description": "프로젝트 범위 필터 (선택사항)"
                },
                "state": {
                    "type": "string",
                    "description": "프로젝트 상태 필터 (선택사항)"
                }
            }
        }
    )


async def get_projects_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for getting projects list."""
    try:
        page = arguments.get("page", 0)
        size = arguments.get("size", 200)
        project_type = arguments.get("type")
        scope = arguments.get("scope")
        state = arguments.get("state")

        kwargs = {}
        if project_type:
            kwargs["type"] = project_type
        if scope:
            kwargs["scope"] = scope
        if state:
            kwargs["state"] = state

        response = await dooray_client.get_projects(page, size, **kwargs)

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "projects": response.get("result", []),
                "totalCount": response.get("totalCount"),
                "message": "프로젝트 목록을 성공적으로 조회했습니다."
            }
            logger.info("Projects retrieved successfully", count=len(response.get("result", [])))
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": "프로젝트 목록 조회에 실패했습니다."
            }
            logger.error("Failed to retrieve projects", error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "프로젝트 목록 조회 중 오류가 발생했습니다."
        }
        logger.error("Exception in get_projects_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def get_project_posts_tool() -> Tool:
    """Tool for getting project posts list."""
    return Tool(
        name="dooray_project_list_posts",
        description="프로젝트의 업무(포스트) 목록을 조회합니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "프로젝트 ID"
                },
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
                "from_member_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "작성자 멤버 ID 목록 (선택사항)"
                },
                "to_member_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "담당자 멤버 ID 목록 (선택사항)"
                },
                "subjects": {
                    "type": "string",
                    "description": "제목 검색 키워드 (선택사항)"
                }
            },
            "required": ["project_id"]
        }
    )


async def get_project_posts_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for getting project posts list."""
    try:
        project_id = arguments["project_id"]
        page = arguments.get("page", 0)
        size = arguments.get("size", 200)

        kwargs = {}
        if "from_member_ids" in arguments:
            kwargs["fromMemberIds"] = arguments["from_member_ids"]
        if "to_member_ids" in arguments:
            kwargs["toMemberIds"] = arguments["to_member_ids"]
        if "subjects" in arguments:
            kwargs["subjects"] = arguments["subjects"]

        response = await dooray_client.get_posts(project_id, page, size, **kwargs)

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "posts": response.get("result", []),
                "totalCount": response.get("totalCount"),
                "message": f"프로젝트 업무 목록을 성공적으로 조회했습니다. (프로젝트: {project_id})"
            }
            logger.info("Project posts retrieved successfully",
                       project_id=project_id,
                       count=len(response.get("result", [])))
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"프로젝트 업무 목록 조회에 실패했습니다. (프로젝트: {project_id})"
            }
            logger.error("Failed to retrieve project posts",
                        project_id=project_id,
                        error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "프로젝트 업무 목록 조회 중 오류가 발생했습니다."
        }
        logger.error("Exception in get_project_posts_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def get_project_post_tool() -> Tool:
    """Tool for getting project post details."""
    return Tool(
        name="dooray_project_get_post",
        description="특정 업무(포스트)의 상세 정보를 조회합니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "프로젝트 ID"
                },
                "post_id": {
                    "type": "string",
                    "description": "업무 ID"
                }
            },
            "required": ["project_id", "post_id"]
        }
    )


async def get_project_post_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for getting project post details."""
    try:
        project_id = arguments["project_id"]
        post_id = arguments["post_id"]

        response = await dooray_client.get_post(project_id, post_id)

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "post": response.get("result"),
                "message": f"업무 상세 정보를 성공적으로 조회했습니다. (업무: {post_id})"
            }
            logger.info("Project post retrieved successfully",
                       project_id=project_id,
                       post_id=post_id)
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"업무 상세 정보 조회에 실패했습니다. (업무: {post_id})"
            }
            logger.error("Failed to retrieve project post",
                        project_id=project_id,
                        post_id=post_id,
                        error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "업무 상세 정보 조회 중 오류가 발생했습니다."
        }
        logger.error("Exception in get_project_post_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def create_project_post_tool() -> Tool:
    """Tool for creating project post."""
    return Tool(
        name="dooray_project_create_post",
        description="새로운 업무(포스트)를 생성합니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "프로젝트 ID"
                },
                "subject": {
                    "type": "string",
                    "description": "업무 제목"
                },
                "body": {
                    "type": "string",
                    "description": "업무 내용"
                },
                "to_member_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "담당자 멤버 ID 목록 (선택사항)"
                },
                "cc_member_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "참조자 멤버 ID 목록 (선택사항)"
                },
                "priority": {
                    "type": "string",
                    "enum": ["high", "normal", "low"],
                    "description": "우선순위 (high/normal/low, 선택사항)"
                }
            },
            "required": ["project_id", "subject", "body"]
        }
    )


async def create_project_post_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for creating project post."""
    try:
        project_id = arguments["project_id"]
        request_data = {
            "subject": arguments["subject"],
            "body": arguments["body"]
        }

        if "to_member_ids" in arguments:
            request_data["toMemberIds"] = arguments["to_member_ids"]
        if "cc_member_ids" in arguments:
            request_data["ccMemberIds"] = arguments["cc_member_ids"]
        if "priority" in arguments:
            request_data["priority"] = arguments["priority"]

        response = await dooray_client.create_post(project_id, request_data)

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "post": response.get("result"),
                "message": f"업무를 성공적으로 생성했습니다. (제목: {arguments['subject']})"
            }
            logger.info("Project post created successfully",
                       project_id=project_id,
                       subject=arguments["subject"])
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"업무 생성에 실패했습니다. (제목: {arguments['subject']})"
            }
            logger.error("Failed to create project post",
                        project_id=project_id,
                        subject=arguments["subject"],
                        error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "업무 생성 중 오류가 발생했습니다."
        }
        logger.error("Exception in create_project_post_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def update_project_post_tool() -> Tool:
    """Tool for updating project post."""
    return Tool(
        name="dooray_project_update_post",
        description="기존 업무(포스트)를 수정합니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "프로젝트 ID"
                },
                "post_id": {
                    "type": "string",
                    "description": "업무 ID"
                },
                "subject": {
                    "type": "string",
                    "description": "새로운 업무 제목 (선택사항)"
                },
                "body": {
                    "type": "string",
                    "description": "새로운 업무 내용 (선택사항)"
                },
                "priority": {
                    "type": "string",
                    "enum": ["high", "normal", "low"],
                    "description": "새로운 우선순위 (high/normal/low, 선택사항)"
                }
            },
            "required": ["project_id", "post_id"]
        }
    )


async def update_project_post_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for updating project post."""
    try:
        project_id = arguments["project_id"]
        post_id = arguments["post_id"]
        request_data = {}

        if "subject" in arguments:
            request_data["subject"] = arguments["subject"]
        if "body" in arguments:
            request_data["body"] = arguments["body"]
        if "priority" in arguments:
            request_data["priority"] = arguments["priority"]

        response = await dooray_client.update_post(project_id, post_id, request_data)

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "message": f"업무를 성공적으로 수정했습니다. (업무: {post_id})"
            }
            logger.info("Project post updated successfully",
                       project_id=project_id,
                       post_id=post_id)
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"업무 수정에 실패했습니다. (업무: {post_id})"
            }
            logger.error("Failed to update project post",
                        project_id=project_id,
                        post_id=post_id,
                        error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "업무 수정 중 오류가 발생했습니다."
        }
        logger.error("Exception in update_project_post_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def set_project_post_workflow_tool() -> Tool:
    """Tool for setting project post workflow."""
    return Tool(
        name="dooray_project_set_post_workflow",
        description="업무(포스트)의 상태(워크플로)를 변경합니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "프로젝트 ID"
                },
                "post_id": {
                    "type": "string",
                    "description": "업무 ID"
                },
                "workflow_id": {
                    "type": "string",
                    "description": "워크플로 ID"
                }
            },
            "required": ["project_id", "post_id", "workflow_id"]
        }
    )


async def set_project_post_workflow_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for setting project post workflow."""
    try:
        project_id = arguments["project_id"]
        post_id = arguments["post_id"]
        workflow_id = arguments["workflow_id"]

        response = await dooray_client.set_post_workflow(project_id, post_id, workflow_id)

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "message": f"업무 상태를 성공적으로 변경했습니다. (업무: {post_id})"
            }
            logger.info("Project post workflow set successfully",
                       project_id=project_id,
                       post_id=post_id,
                       workflow_id=workflow_id)
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"업무 상태 변경에 실패했습니다. (업무: {post_id})"
            }
            logger.error("Failed to set project post workflow",
                        project_id=project_id,
                        post_id=post_id,
                        workflow_id=workflow_id,
                        error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "업무 상태 변경 중 오류가 발생했습니다."
        }
        logger.error("Exception in set_project_post_workflow_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def set_project_post_done_tool() -> Tool:
    """Tool for setting project post as done."""
    return Tool(
        name="dooray_project_set_post_done",
        description="업무(포스트)를 완료 상태로 변경합니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "프로젝트 ID"
                },
                "post_id": {
                    "type": "string",
                    "description": "업무 ID"
                }
            },
            "required": ["project_id", "post_id"]
        }
    )


async def set_project_post_done_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for setting project post as done."""
    try:
        project_id = arguments["project_id"]
        post_id = arguments["post_id"]

        response = await dooray_client.set_post_done(project_id, post_id)

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "message": f"업무를 성공적으로 완료 처리했습니다. (업무: {post_id})"
            }
            logger.info("Project post set as done successfully",
                       project_id=project_id,
                       post_id=post_id)
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"업무 완료 처리에 실패했습니다. (업무: {post_id})"
            }
            logger.error("Failed to set project post as done",
                        project_id=project_id,
                        post_id=post_id,
                        error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "업무 완료 처리 중 오류가 발생했습니다."
        }
        logger.error("Exception in set_project_post_done_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


# Comment tools

def create_post_comment_tool() -> Tool:
    """Tool for creating post comment."""
    return Tool(
        name="dooray_project_create_post_comment",
        description="업무(포스트)에 댓글을 생성합니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "프로젝트 ID"
                },
                "post_id": {
                    "type": "string",
                    "description": "업무 ID"
                },
                "content": {
                    "type": "string",
                    "description": "댓글 내용"
                },
                "mime_type": {
                    "type": "string",
                    "description": "댓글 타입 (기본값: text/x-markdown)",
                    "default": "text/x-markdown"
                }
            },
            "required": ["project_id", "post_id", "content"]
        }
    )


async def create_post_comment_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for creating post comment."""
    try:
        project_id = arguments["project_id"]
        post_id = arguments["post_id"]
        request_data = {
            "content": arguments["content"],
            "mimeType": arguments.get("mime_type", "text/x-markdown")
        }

        response = await dooray_client.create_post_comment(project_id, post_id, request_data)

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "comment": response.get("result"),
                "message": f"업무 댓글을 성공적으로 생성했습니다. (업무: {post_id})"
            }
            logger.info("Post comment created successfully",
                       project_id=project_id,
                       post_id=post_id)
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"업무 댓글 생성에 실패했습니다. (업무: {post_id})"
            }
            logger.error("Failed to create post comment",
                        project_id=project_id,
                        post_id=post_id,
                        error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "업무 댓글 생성 중 오류가 발생했습니다."
        }
        logger.error("Exception in create_post_comment_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def get_post_comments_tool() -> Tool:
    """Tool for getting post comments."""
    return Tool(
        name="dooray_project_get_post_comments",
        description="업무(포스트)의 댓글 목록을 조회합니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "프로젝트 ID"
                },
                "post_id": {
                    "type": "string",
                    "description": "업무 ID"
                },
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
                "order": {
                    "type": "string",
                    "description": "정렬 순서 (asc/desc, 선택사항)"
                }
            },
            "required": ["project_id", "post_id"]
        }
    )


async def get_post_comments_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for getting post comments."""
    try:
        project_id = arguments["project_id"]
        post_id = arguments["post_id"]
        page = arguments.get("page", 0)
        size = arguments.get("size", 200)
        order = arguments.get("order")

        response = await dooray_client.get_post_comments(project_id, post_id, page, size, order)

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "comments": response.get("result", []),
                "totalCount": response.get("totalCount"),
                "message": f"업무 댓글 목록을 성공적으로 조회했습니다. (업무: {post_id})"
            }
            logger.info("Post comments retrieved successfully",
                       project_id=project_id,
                       post_id=post_id,
                       count=len(response.get("result", [])))
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"업무 댓글 목록 조회에 실패했습니다. (업무: {post_id})"
            }
            logger.error("Failed to retrieve post comments",
                        project_id=project_id,
                        post_id=post_id,
                        error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "업무 댓글 목록 조회 중 오류가 발생했습니다."
        }
        logger.error("Exception in get_post_comments_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def update_post_comment_tool() -> Tool:
    """Tool for updating post comment."""
    return Tool(
        name="dooray_project_update_post_comment",
        description="업무(포스트) 댓글을 수정합니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "프로젝트 ID"
                },
                "post_id": {
                    "type": "string",
                    "description": "업무 ID"
                },
                "log_id": {
                    "type": "string",
                    "description": "댓글 ID"
                },
                "content": {
                    "type": "string",
                    "description": "새로운 댓글 내용"
                },
                "mime_type": {
                    "type": "string",
                    "description": "댓글 타입 (기본값: text/x-markdown)",
                    "default": "text/x-markdown"
                }
            },
            "required": ["project_id", "post_id", "log_id", "content"]
        }
    )


async def update_post_comment_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for updating post comment."""
    try:
        project_id = arguments["project_id"]
        post_id = arguments["post_id"]
        log_id = arguments["log_id"]
        request_data = {
            "content": arguments["content"],
            "mimeType": arguments.get("mime_type", "text/x-markdown")
        }

        response = await dooray_client.update_post_comment(project_id, post_id, log_id, request_data)

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "message": f"업무 댓글을 성공적으로 수정했습니다. (댓글: {log_id})"
            }
            logger.info("Post comment updated successfully",
                       project_id=project_id,
                       post_id=post_id,
                       log_id=log_id)
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"업무 댓글 수정에 실패했습니다. (댓글: {log_id})"
            }
            logger.error("Failed to update post comment",
                        project_id=project_id,
                        post_id=post_id,
                        log_id=log_id,
                        error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "업무 댓글 수정 중 오류가 발생했습니다."
        }
        logger.error("Exception in update_post_comment_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def delete_post_comment_tool() -> Tool:
    """Tool for deleting post comment."""
    return Tool(
        name="dooray_project_delete_post_comment",
        description="업무(포스트) 댓글을 삭제합니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "프로젝트 ID"
                },
                "post_id": {
                    "type": "string",
                    "description": "업무 ID"
                },
                "log_id": {
                    "type": "string",
                    "description": "댓글 ID"
                }
            },
            "required": ["project_id", "post_id", "log_id"]
        }
    )


async def delete_post_comment_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for deleting post comment."""
    try:
        project_id = arguments["project_id"]
        post_id = arguments["post_id"]
        log_id = arguments["log_id"]

        response = await dooray_client.delete_post_comment(project_id, post_id, log_id)

        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "message": f"업무 댓글을 성공적으로 삭제했습니다. (댓글: {log_id})"
            }
            logger.info("Post comment deleted successfully",
                       project_id=project_id,
                       post_id=post_id,
                       log_id=log_id)
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"업무 댓글 삭제에 실패했습니다. (댓글: {log_id})"
            }
            logger.error("Failed to delete post comment",
                        project_id=project_id,
                        post_id=post_id,
                        log_id=log_id,
                        error=result["error"])

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "업무 댓글 삭제 중 오류가 발생했습니다."
        }
        logger.error("Exception in delete_post_comment_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]

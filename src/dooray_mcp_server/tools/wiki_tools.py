"""Wiki-related MCP tools."""

import json
from typing import Any, Dict, Sequence

from mcp.types import Tool
import structlog

from ..client.dooray_client import DoorayClient

logger = structlog.get_logger(__name__)


def get_wikis_tool() -> Tool:
    """Tool for getting list of wiki projects."""
    return Tool(
        name="dooray_wiki_list_projects",
        description="두레이에서 접근 가능한 위키 프로젝트 목록을 조회합니다. 특정 프로젝트의 이름으로 프로젝트 ID를 찾을 때 사용하세요.",
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
                }
            }
        }
    )


async def get_wikis_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for getting wikis list."""
    try:
        page = arguments.get("page", 0)
        size = arguments.get("size", 200)
        
        response = await dooray_client.get_wikis(page, size)
        
        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "wikis": response.get("result", []),
                "totalCount": response.get("totalCount"),
                "message": "위키 프로젝트 목록을 성공적으로 조회했습니다."
            }
            logger.info("Wiki projects retrieved successfully", count=len(response.get("result", [])))
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": "위키 프로젝트 목록 조회에 실패했습니다."
            }
            logger.error("Failed to retrieve wiki projects", error=result["error"])
            
        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "위키 프로젝트 목록 조회 중 오류가 발생했습니다."
        }
        logger.error("Exception in get_wikis_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def get_wiki_pages_tool() -> Tool:
    """Tool for getting list of wiki pages."""
    return Tool(
        name="dooray_wiki_list_pages",
        description="특정 두레이 위키 프로젝트의 페이지 목록을 조회합니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "위키 프로젝트 ID"
                },
                "parent_page_id": {
                    "type": "string",
                    "description": "상위 페이지 ID (선택사항, 자식 페이지만 조회)"
                }
            },
            "required": ["project_id"]
        }
    )


async def get_wiki_pages_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for getting wiki pages list."""
    try:
        project_id = arguments["project_id"]
        parent_page_id = arguments.get("parent_page_id")
        
        response = await dooray_client.get_wiki_pages(project_id, parent_page_id)
        
        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "pages": response.get("result", []),
                "totalCount": response.get("totalCount"),
                "message": f"위키 페이지 목록을 성공적으로 조회했습니다. (프로젝트: {project_id})"
            }
            logger.info("Wiki pages retrieved successfully", 
                       project_id=project_id, 
                       count=len(response.get("result", [])))
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"위키 페이지 목록 조회에 실패했습니다. (프로젝트: {project_id})"
            }
            logger.error("Failed to retrieve wiki pages", 
                        project_id=project_id, 
                        error=result["error"])
            
        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "위키 페이지 목록 조회 중 오류가 발생했습니다."
        }
        logger.error("Exception in get_wiki_pages_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def get_wiki_page_tool() -> Tool:
    """Tool for getting wiki page details."""
    return Tool(
        name="dooray_wiki_get_page",
        description="특정 두레이 위키 페이지의 상세 정보를 조회합니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "위키 프로젝트 ID"
                },
                "page_id": {
                    "type": "string", 
                    "description": "위키 페이지 ID"
                }
            },
            "required": ["project_id", "page_id"]
        }
    )


async def get_wiki_page_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for getting wiki page details."""
    try:
        project_id = arguments["project_id"]
        page_id = arguments["page_id"]
        
        response = await dooray_client.get_wiki_page(project_id, page_id)
        
        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "page": response.get("result"),
                "message": f"위키 페이지를 성공적으로 조회했습니다. (페이지: {page_id})"
            }
            logger.info("Wiki page retrieved successfully", 
                       project_id=project_id, 
                       page_id=page_id)
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"위키 페이지 조회에 실패했습니다. (페이지: {page_id})"
            }
            logger.error("Failed to retrieve wiki page", 
                        project_id=project_id, 
                        page_id=page_id,
                        error=result["error"])
            
        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "위키 페이지 조회 중 오류가 발생했습니다."
        }
        logger.error("Exception in get_wiki_page_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def create_wiki_page_tool() -> Tool:
    """Tool for creating wiki page."""
    return Tool(
        name="dooray_wiki_create_page",
        description="새로운 위키 페이지를 생성합니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "wiki_id": {
                    "type": "string",
                    "description": "위키 프로젝트 ID"
                },
                "title": {
                    "type": "string",
                    "description": "위키 페이지 제목"
                },
                "content": {
                    "type": "string",
                    "description": "위키 페이지 내용"
                },
                "parent_page_id": {
                    "type": "string",
                    "description": "상위 페이지 ID (선택사항)"
                }
            },
            "required": ["wiki_id", "title", "content"]
        }
    )


async def create_wiki_page_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for creating wiki page."""
    try:
        wiki_id = arguments["wiki_id"]
        request_data = {
            "title": arguments["title"],
            "content": arguments["content"]
        }
        
        if "parent_page_id" in arguments:
            request_data["parentPageId"] = arguments["parent_page_id"]
        
        response = await dooray_client.create_wiki_page(wiki_id, request_data)
        
        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "page": response.get("result"),
                "message": f"위키 페이지를 성공적으로 생성했습니다. (제목: {arguments['title']})"
            }
            logger.info("Wiki page created successfully", 
                       wiki_id=wiki_id, 
                       title=arguments["title"])
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"위키 페이지 생성에 실패했습니다. (제목: {arguments['title']})"
            }
            logger.error("Failed to create wiki page", 
                        wiki_id=wiki_id, 
                        title=arguments["title"],
                        error=result["error"])
            
        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "위키 페이지 생성 중 오류가 발생했습니다."
        }
        logger.error("Exception in create_wiki_page_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]


def update_wiki_page_tool() -> Tool:
    """Tool for updating wiki page."""
    return Tool(
        name="dooray_wiki_update_page",
        description="기존의 위키 페이지를 수정합니다.",
        inputSchema={
            "type": "object",
            "properties": {
                "wiki_id": {
                    "type": "string",
                    "description": "위키 프로젝트 ID"
                },
                "page_id": {
                    "type": "string",
                    "description": "수정할 위키 페이지 ID"
                },
                "title": {
                    "type": "string",
                    "description": "새로운 위키 페이지 제목 (선택사항)"
                },
                "content": {
                    "type": "string",
                    "description": "새로운 위키 페이지 내용 (선택사항)"
                }
            },
            "required": ["wiki_id", "page_id"]
        }
    )


async def update_wiki_page_handler(dooray_client: DoorayClient, arguments: Dict[str, Any]) -> Sequence[Any]:
    """Handler for updating wiki page."""
    try:
        wiki_id = arguments["wiki_id"]
        page_id = arguments["page_id"]
        request_data = {}
        
        if "title" in arguments:
            request_data["title"] = arguments["title"]
        if "content" in arguments:
            request_data["content"] = arguments["content"]
        
        response = await dooray_client.update_wiki_page(wiki_id, page_id, request_data)
        
        if response.get("header", {}).get("isSuccessful"):
            result = {
                "success": True,
                "message": f"위키 페이지를 성공적으로 수정했습니다. (페이지: {page_id})"
            }
            logger.info("Wiki page updated successfully", 
                       wiki_id=wiki_id, 
                       page_id=page_id)
        else:
            result = {
                "success": False,
                "error": response.get("header", {}).get("resultMessage", "Unknown error"),
                "message": f"위키 페이지 수정에 실패했습니다. (페이지: {page_id})"
            }
            logger.error("Failed to update wiki page", 
                        wiki_id=wiki_id, 
                        page_id=page_id,
                        error=result["error"])
            
        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "위키 페이지 수정 중 오류가 발생했습니다."
        }
        logger.error("Exception in update_wiki_page_handler", error=str(e))
        return [{"type": "text", "text": json.dumps(error_result, ensure_ascii=False, indent=2)}]
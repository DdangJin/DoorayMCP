# 🚀 Dooray MCP Server (Python + Streamable HTTP)

Python 기반 Dooray MCP 서버로, **Streamable HTTP Transport**와 기존 **STDIO Transport**를 모두 지원합니다.

## ✨ 주요 특징

- 🐍 **Python 3.10+ 지원**
- 🌐 **Streamable HTTP Transport** - 웹 기반 MCP 클라이언트 지원  
- 📡 **STDIO Transport** - Claude Desktop 등 기존 클라이언트 지원
- ⚡ **FastAPI 기반** - 고성능 비동기 HTTP 서버
- 🔒 **보안 기능** - Origin 검증, CORS 보호, 세션 관리
- 📊 **28개 도구** - Wiki, 프로젝트, 메신저, 캘린더 API 완전 지원
- 🛠️ **uvx 지원** - 가상환경 없이 즉시 실행

## 🚀 빠른 시작 (uvx 사용, 추천)

### 1. 환경변수 설정
```bash
export DOORAY_API_KEY="your_api_key_here"
export DOORAY_BASE_URL="https://api.dooray.com"
```

### 2. uvx로 즉시 실행

#### HTTP 모드 (Streamable HTTP Transport)
```bash
# Git 저장소에서 직접 실행
uvx --from git+https://github.com/your-username/DoorayMCP dooray-mcp-server-http

# 로컬 클론한 프로젝트에서 실행  
uvx --from . dooray-mcp-server-http

# 커스텀 설정으로 실행
uvx --from . dooray-mcp-server-http --host 127.0.0.1 --port 8080
```

#### STDIO 모드 (Claude Desktop 호환)
```bash
uvx --from . dooray-mcp-server
```

## 🐍 전통적인 Python 설치 방법

### 1. 가상환경 설정
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows
```

### 2. 프로젝트 설치
```bash
pip install -e .
# 또는 개발 의존성 포함
pip install -e ".[dev]"
```

### 3. 실행
```bash
# HTTP 모드
python -m dooray_mcp_server.main_http
dooray-mcp-server-http  # 설치 후

# STDIO 모드  
python -m dooray_mcp_server.main
dooray-mcp-server  # 설치 후
```

## 🖥️ Claude Desktop 설정

### uvx 사용 (추천)
```json
{
  "mcpServers": {
    "dooray-mcp": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/your-username/DoorayMCP",
        "dooray-mcp-server-http",
        "--port", "8080"
      ],
      "env": {
        "DOORAY_API_KEY": "your_api_key_here",
        "DOORAY_BASE_URL": "https://api.dooray.com"
      }
    }
  }
}
```

### 로컬 개발용
```json
{
  "mcpServers": {
    "dooray-mcp-local": {
      "command": "uvx",
      "args": [
        "--from", "/Users/username/path/to/DoorayMCP",
        "dooray-mcp-server-http"
      ],
      "env": {
        "DOORAY_API_KEY": "your_api_key_here",
        "DOORAY_BASE_URL": "https://api.dooray.com",
        "DOORAY_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## 🌐 HTTP API 사용법

### 서버 상태 확인
```bash
curl http://localhost:8080/health
# 응답: {"status": "healthy", "server": "dooray-mcp-server"}
```

### MCP 도구 목록 조회
```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

### 도구 실행 예제
```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "dooray_wiki_list_projects",
      "arguments": {
        "page": 0,
        "size": 10
      }
    }
  }'
```

### Server-Sent Events 스트리밍
```bash
curl -N -H "Accept: text/event-stream" http://localhost:8080/mcp
```

## 🐳 Docker 실행

### 이미지 빌드 및 실행
```bash
# 빌드
docker build -f Dockerfile.python -t dooray-mcp-python .

# 실행
docker run -p 8080:8080 \
  -e DOORAY_API_KEY="your_api_key" \
  -e DOORAY_BASE_URL="https://api.dooray.com" \
  dooray-mcp-python
```

## 📊 지원하는 도구 (28개)

### 🗂️ Wiki 도구 (5개)
- `dooray_wiki_list_projects` - Wiki 프로젝트 목록
- `dooray_wiki_list_pages` - Wiki 페이지 목록  
- `dooray_wiki_get_page` - Wiki 페이지 상세
- `dooray_wiki_create_page` - Wiki 페이지 생성
- `dooray_wiki_update_page` - Wiki 페이지 수정

### 📋 프로젝트 도구 (7개)
- `dooray_project_list_projects` - 프로젝트 목록
- `dooray_project_list_posts` - 업무 목록
- `dooray_project_get_post` - 업무 상세
- `dooray_project_create_post` - 업무 생성
- `dooray_project_update_post` - 업무 수정
- `dooray_project_set_post_workflow` - 업무 상태 변경
- `dooray_project_set_post_done` - 업무 완료

### 💬 댓글 도구 (4개)
- `dooray_project_create_post_comment` - 댓글 생성
- `dooray_project_get_post_comments` - 댓글 목록
- `dooray_project_update_post_comment` - 댓글 수정
- `dooray_project_delete_post_comment` - 댓글 삭제

### 💌 메신저 도구 (7개)
- `dooray_messenger_search_members` - 멤버 검색
- `dooray_messenger_send_direct_message` - DM 전송
- `dooray_messenger_get_channels` - 채널 목록
- `dooray_messenger_get_simple_channels` - 간단 채널 목록
- `dooray_messenger_get_channel` - 채널 상세
- `dooray_messenger_create_channel` - 채널 생성
- `dooray_messenger_send_channel_message` - 채널 메시지

### 📅 캘린더 도구 (5개)
- `dooray_calendar_list` - 캘린더 목록
- `dooray_calendar_detail` - 캘린더 상세  
- `dooray_calendar_events` - 일정 목록
- `dooray_calendar_event_detail` - 일정 상세
- `dooray_calendar_create_event` - 일정 생성

## ⚙️ 설정 옵션

### 환경변수
| 변수명 | 설명 | 기본값 | 필수 |
|--------|------|--------|------|
| `DOORAY_API_KEY` | Dooray API 키 | - | ✅ |
| `DOORAY_BASE_URL` | Dooray API URL | - | ✅ |
| `DOORAY_LOG_LEVEL` | 로그 레벨 | WARN | ❌ |
| `DOORAY_HTTP_LOG_LEVEL` | HTTP 로그 레벨 | WARN | ❌ |

### CLI 옵션 (HTTP 모드)
```bash
dooray-mcp-server-http \
  --host 127.0.0.1 \        # 바인드 호스트
  --port 8080 \             # 포트 번호  
  --path /mcp \             # MCP 엔드포인트 경로
  --env-file .env           # 환경변수 파일
```

## 🔧 개발

### 개발 명령어

#### 설정 및 설치
```bash
# 개발 의존성과 함께 설치
pip install -e ".[dev]"

# 가상환경 없이 즉시 실행하려면 uvx 사용
uvx --from . dooray-mcp-server-streamable
```

#### 서버 실행 (4가지 전송 방식)

**1. STDIO 모드 (Claude Desktop용)**
```bash
# Python 모듈로 실행
python -m dooray_mcp_server.main
# 또는 설치 후:
dooray-mcp-server
# 또는 uv 사용:
uv run dooray-mcp-server
```

**2. Streamable HTTP 모드 (MCP 표준 준수, 권장)**
```bash
# Python 모듈로 실행
python -m dooray_mcp_server.main_streamable_http
# 또는 설치 후:
dooray-mcp-server-streamable --host 127.0.0.1 --port 8080
# 또는 uv 사용:
uv run dooray-mcp-server-streamable --port 8080
```

**3. SSE 모드 (Server-Sent Events)**
```bash
# Python 모듈로 실행
python -m dooray_mcp_server.main_sse
# 또는 설치 후:
dooray-mcp-server-sse --host 127.0.0.1 --port 8080
# 또는 uv 사용:
uv run dooray-mcp-server-sse --port 8080
```

**4. HTTP 모드 (레거시, 호환성용)**
```bash
# Python 모듈로 실행
python -m dooray_mcp_server.main_http
# 또는 설치 후:
dooray-mcp-server-http --host 127.0.0.1 --port 8080
# 또는 uv 사용:
uv run dooray-mcp-server-http --port 8080
```

### 테스트 실행
```bash
pytest                    # 단위 테스트
pytest --cov=dooray_mcp_server  # 커버리지 포함
```

### 코드 품질
```bash
black src/               # 코드 포맷팅
isort src/               # import 정리
ruff check src/          # 린팅
mypy src/                # 타입 체크
```

## 🎯 uvx 사용법 상세

uvx를 사용하면 가상환경 설정 없이 바로 실행할 수 있습니다:

```bash
# Git에서 직접 실행
uvx --from git+https://github.com/user/DoorayMCP dooray-mcp-server-http

# 로컬 소스에서 실행  
uvx --from . dooray-mcp-server-http --port 8080

# 환경변수 파일과 함께
uvx --from . dooray-mcp-server-http --env-file .env

# 디버그 모드
DOORAY_LOG_LEVEL=DEBUG uvx --from . dooray-mcp-server-http
```

자세한 uvx 사용법은 [README-uvx.md](README-uvx.md) 참조

## 🐛 문제 해결

### 자주 발생하는 문제
1. **환경변수 오류**: `.env` 파일 또는 export로 설정 확인
2. **포트 충돌**: 다른 포트 사용 (`--port 8081`)  
3. **API 인증 실패**: Dooray API 키 확인
4. **uvx 실행 실패**: `uv --version`으로 설치 확인

### 디버깅
```bash
# 상세 로그 활성화
export DOORAY_LOG_LEVEL=DEBUG
uvx --from . dooray-mcp-server-http

# 헬스체크
curl http://localhost:8080/health
```

## 📚 추가 문서

- [uvx 실행 가이드](README-uvx.md)
- [실행 예제 모음](run-examples.md) 
- [Python 버전 상세 가이드](README-python.md)

## 🔗 참고 링크

- [Dooray API 문서](https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [uvx 공식 문서](https://docs.astral.sh/uv/guides/tools/)

## 📄 라이선스

MIT License

---

**🎉 완전한 Python MCP 서버가 준비되었습니다!**  
uvx로 간편하게 실행하거나, 전통적인 pip 설치로 사용하세요.
# Dooray MCP Server (Python)

Python 기반 Dooray MCP 서버로, **Streamable HTTP Transport**를 지원합니다.

## 주요 특징

- 🐍 **Python 3.10+ 지원**
- 🌐 **Streamable HTTP Transport** - 웹 기반 MCP 클라이언트 지원
- 📡 **전통적인 STDIO Transport** - Claude Desktop 등 기존 클라이언트 지원
- ⚡ **FastAPI 기반** - 고성능 비동기 HTTP 서버
- 🔒 **보안 기능** - Origin 검증, CORS 보호
- 📊 **28개 도구** - Wiki, 프로젝트, 메신저, 캘린더 API 지원

## 빠른 시작

### 1. 환경 설정

```bash
# Python 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt

# 또는 개발 의존성 포함 설치
pip install -e ".[dev]"
```

### 2. 환경변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
DOORAY_API_KEY=your_api_key_here
DOORAY_BASE_URL=https://api.dooray.com
```

### 3. 서버 실행

#### HTTP 서버 (Streamable HTTP Transport)

```bash
# 개발 모드
python -m dooray_mcp_server.main_http

# 또는 설치된 명령어 사용
dooray-mcp-server-http

# 커스텀 설정
dooray-mcp-server-http --host 0.0.0.0 --port 9000 --path /api/mcp
```

#### STDIO 서버 (전통적인 모드)

```bash
# 개발 모드
python -m dooray_mcp_server.main

# 또는 설치된 명령어 사용
dooray-mcp-server
```

## Streamable HTTP 사용법

### Claude Desktop 설정

HTTP 모드는 웹 기반 MCP 클라이언트와 함께 사용하거나, 원격 MCP 서버로 실행할 수 있습니다.

```json
{
  "mcpServers": {
    "dooray-mcp-http": {
      "command": "python",
      "args": [
        "-m", "dooray_mcp_server.main_http",
        "--host", "127.0.0.1",
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

### 직접 HTTP API 호출

서버가 실행되면 HTTP API를 통해 직접 호출할 수 있습니다:

```bash
# 서버 상태 확인
curl http://localhost:8080/health

# 도구 목록 조회
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

# 도구 실행
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

### Server-Sent Events (SSE) 스트리밍

```bash
# SSE 스트림 연결
curl -N -H "Accept: text/event-stream" http://localhost:8080/mcp
```

## Docker 실행

### 이미지 빌드

```bash
docker build -f Dockerfile.python -t dooray-mcp-python .
```

### 컨테이너 실행

```bash
# HTTP 모드
docker run -p 8080:8080 \
  -e DOORAY_API_KEY="your_api_key" \
  -e DOORAY_BASE_URL="https://api.dooray.com" \
  dooray-mcp-python

# STDIO 모드
docker run -i \
  -e DOORAY_API_KEY="your_api_key" \
  -e DOORAY_BASE_URL="https://api.dooray.com" \
  dooray-mcp-python dooray-mcp-server
```

## 설정 옵션

### 환경변수

| 변수명 | 설명 | 기본값 | 필수 |
|--------|------|--------|------|
| `DOORAY_API_KEY` | Dooray API 키 | - | ✅ |
| `DOORAY_BASE_URL` | Dooray API 베이스 URL | - | ✅ |
| `DOORAY_LOG_LEVEL` | 로그 레벨 (DEBUG/INFO/WARN/ERROR) | WARN | ❌ |
| `DOORAY_HTTP_LOG_LEVEL` | HTTP 로그 레벨 | WARN | ❌ |

### 명령행 인수 (HTTP 모드)

```bash
dooray-mcp-server-http \
  --host 0.0.0.0 \      # 바인드 호스트 (기본: 127.0.0.1)
  --port 9000 \         # 포트 번호 (기본: 8080)
  --path /api/mcp \     # MCP 엔드포인트 경로 (기본: /mcp)
  --env-file .env       # 환경변수 파일 경로 (기본: .env)
```

## 지원하는 도구 (28개)

### Wiki 관련 도구 (5개)
- `dooray_wiki_list_projects` - Wiki 프로젝트 목록 조회
- `dooray_wiki_list_pages` - Wiki 페이지 목록 조회
- `dooray_wiki_get_page` - Wiki 페이지 상세 조회
- `dooray_wiki_create_page` - Wiki 페이지 생성
- `dooray_wiki_update_page` - Wiki 페이지 수정

### 프로젝트 관련 도구 (7개)
- `dooray_project_list_projects` - 프로젝트 목록 조회
- `dooray_project_list_posts` - 업무 목록 조회
- `dooray_project_get_post` - 업무 상세 조회
- `dooray_project_create_post` - 업무 생성
- `dooray_project_update_post` - 업무 수정
- `dooray_project_set_post_workflow` - 업무 상태 변경
- `dooray_project_set_post_done` - 업무 완료 처리

### 댓글 관련 도구 (4개)
- `dooray_project_create_post_comment` - 업무 댓글 생성
- `dooray_project_get_post_comments` - 업무 댓글 목록 조회
- `dooray_project_update_post_comment` - 업무 댓글 수정
- `dooray_project_delete_post_comment` - 업무 댓글 삭제

### 메신저 관련 도구 (7개)
- `dooray_messenger_search_members` - 멤버 검색
- `dooray_messenger_send_direct_message` - 다이렉트 메시지 전송
- `dooray_messenger_get_channels` - 채널 목록 조회
- `dooray_messenger_get_simple_channels` - 간소화된 채널 목록 조회
- `dooray_messenger_get_channel` - 채널 상세 조회
- `dooray_messenger_create_channel` - 채널 생성
- `dooray_messenger_send_channel_message` - 채널 메시지 전송

### 캘린더 관련 도구 (5개)
- `dooray_calendar_list` - 캘린더 목록 조회
- `dooray_calendar_detail` - 캘린더 상세 조회
- `dooray_calendar_events` - 캘린더 이벤트 조회
- `dooray_calendar_event_detail` - 캘린더 이벤트 상세 조회
- `dooray_calendar_create_event` - 캘린더 이벤트 생성

## 개발

### 테스트 실행

```bash
# 단위 테스트
pytest

# 커버리지 포함
pytest --cov=dooray_mcp_server

# 통합 테스트 (환경변수 필요)
pytest tests/integration/
```

### 코드 품질 검사

```bash
# 코드 포맷팅
black src/
isort src/

# 린팅
ruff check src/

# 타입 체크
mypy src/
```

## MCP Protocol 구현

이 서버는 Model Context Protocol의 다음 기능들을 구현합니다:

### Streamable HTTP Transport
- HTTP POST/GET 요청 지원
- Server-Sent Events (SSE) 스트리밍
- 세션 관리 (`Mcp-Session-Id` 헤더)
- CORS 보안 설정
- Origin 검증

### JSON-RPC 메서드
- `initialize` - MCP 세션 초기화
- `tools/list` - 사용 가능한 도구 목록 반환
- `tools/call` - 특정 도구 실행

### 보안 기능
- Origin 헤더 검증으로 DNS rebinding 공격 방지
- localhost/127.0.0.1만 허용하는 CORS 정책
- 세션 기반 요청 추적

## 문제 해결

### 자주 발생하는 오류

1. **환경변수 오류**
   ```
   ValueError: DOORAY_API_KEY environment variable is required
   ```
   → `.env` 파일을 확인하고 필요한 환경변수가 설정되어 있는지 확인

2. **포트 충돌**
   ```
   OSError: [Errno 48] Address already in use
   ```
   → 다른 포트를 사용하거나 실행 중인 프로세스 종료

3. **API 인증 실패**
   ```
   HTTP 401 Unauthorized
   ```
   → Dooray API 키가 올바른지 확인

### 로그 레벨 조정

디버깅을 위해 로그 레벨을 높일 수 있습니다:

```bash
export DOORAY_LOG_LEVEL=DEBUG
export DOORAY_HTTP_LOG_LEVEL=DEBUG
dooray-mcp-server-http
```

## 라이선스

MIT License

## 기여

이슈 및 Pull Request를 환영합니다!
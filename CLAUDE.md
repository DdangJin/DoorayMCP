# CLAUDE.md

이 파일은 이 저장소에서 작업할 때 Claude Code (claude.ai/code)에게 가이드를 제공합니다.

## 저장소 소개

이 저장소는 Dooray API 통합을 위한 Python 기반 MCP (Model Context Protocol) 서버입니다. kotlin 기반의 `sungmin-koo-ai/DoorayMCP`에서 포크되었으며, python으로 변환한 저장소입니다. 이중 전송 지원(STDIO 및 HTTP)으로 MCP 표준을 구현하고 Dooray의 Wiki, 프로젝트, 메신저, 캘린더 API에 접근하는 28개 도구를 제공합니다.

## 아키텍처

### 핵심 구성 요소

- **서버 레이어** (`src/dooray_mcp_server/server.py`): HTTP와 STDIO 서버 모드를 조율하는 메인 `DoorayMcpServer` 클래스
- **전송 레이어** (`src/dooray_mcp_server/transport/`): FastAPI와 SSE 지원으로 스트리머블 HTTP 프로토콜을 구현하는 HTTP 서버 전송
- **클라이언트 레이어** (`src/dooray_mcp_server/client/`): 비동기 httpx를 사용한 Dooray API 통신용 HTTP 클라이언트
- **도구 레이어** (`src/dooray_mcp_server/tools/`): Dooray 서비스별로 구성된 28개 MCP 도구 (wiki, project, messenger, calendar)

### 이중 전송 아키텍처

서버는 두 가지 전송 모드를 지원합니다:
- **STDIO 모드**: Claude Desktop 통합을 위한 전통적인 MCP 전송
- **HTTP 모드**: 웹 클라이언트를 위한 FastAPI, CORS, SSE를 사용한 스트리머블 HTTP 전송

진입점이 분리되어 있습니다: `main.py` (STDIO), `main_http.py` (HTTP).

## 개발 명령어

### 설정 및 설치
```bash
# 개발 의존성과 함께 설치
pip install -e ".[dev]"

# 가상환경 없이 즉시 실행하려면 uvx 사용
uvx --from . dooray-mcp-server-http
```

### 서버 실행
```bash
# HTTP 모드 (권장)
python -m dooray_mcp_server.main_http
# 또는 설치 후:
dooray-mcp-server-http --host 127.0.0.1 --port 8080

# STDIO 모드 (Claude Desktop용)
python -m dooray_mcp_server.main
# 또는 설치 후:
dooray-mcp-server
```

### 테스트
```bash
# 모든 테스트 실행
pytest

# 커버리지 포함 실행
pytest --cov=dooray_mcp_server

# 특정 테스트 파일 실행
pytest tests/test_server.py
```

### 코드 품질
```bash
# 코드 포맷팅
black src/

# import 정리
isort src/

# 코드 린팅
ruff check src/

# 타입 체크
mypy src/
```

### Docker
```bash
# 이미지 빌드
docker build -f Dockerfile -t dooray-mcp-python .

# 컨테이너 실행
docker run -p 8080:8080 \
  -e DOORAY_API_KEY="your_key" \
  -e DOORAY_BASE_URL="https://api.dooray.com" \
  dooray-mcp-python
```

## 필수 환경 변수

```bash
export DOORAY_API_KEY="your_api_key_here"
export DOORAY_BASE_URL="https://api.dooray.com"
```

선택적 변수:
- `DOORAY_LOG_LEVEL`: DEBUG, INFO, WARN (기본값), ERROR
- `DOORAY_HTTP_LOG_LEVEL`: HTTP 전용 로깅 레벨

## 도구 아키텍처

도구는 별도 모듈에서 Dooray 서비스별로 구성됩니다:
- `wiki_tools.py`: 5개 위키 관리 도구
- `project_tools.py`: 11개 프로젝트/업무 관리 도구 (댓글 포함)
- `messenger_tools.py`: 7개 메시징 및 채널 도구
- `calendar_tools.py`: 5개 캘린더 및 일정 도구

각 도구 모듈은 다음 패턴을 따릅니다:
- 입력/출력 스키마를 가진 도구 정의
- 비즈니스 로직을 구현하는 핸들러 함수
- `tools/__init__.py`에서 등록

## HTTP API 엔드포인트

HTTP 모드에서 실행할 때:
- `GET /health`: 서버 상태 확인
- `POST /mcp`: MCP JSON-RPC 엔드포인트
- `GET /mcp`: Server-Sent Events 스트리밍 엔드포인트

## uvx 통합

프로젝트는 가상환경 없이 uvx 실행이 가능하도록 설계되었습니다:
```bash
# Git에서 직접 실행
uvx --from git+https://github.com/user/DoorayMCP dooray-mcp-server-http

# 로컬 개발
uvx --from . dooray-mcp-server-http --port 8080
```
# Dooray MCP Server 실행 예제

다양한 방법으로 Dooray MCP 서버를 실행하는 예제들입니다.

## 🚀 uvx를 사용한 실행 (추천)

### 기본 HTTP 서버 실행
```bash
# Git 저장소에서 직접 실행
uvx --from git+https://github.com/your-username/DoorayMCP dooray-mcp-server-http

# 로컬 소스에서 실행
uvx --from . dooray-mcp-server-http
```

### 환경변수와 함께 실행
```bash
export DOORAY_API_KEY="your_api_key"
export DOORAY_BASE_URL="https://api.dooray.com"
uvx --from . dooray-mcp-server-http --port 8080
```

### 커스텀 설정으로 실행
```bash
uvx --from . dooray-mcp-server-http \
  --host 0.0.0.0 \
  --port 9000 \
  --path /api/mcp \
  --env-file .env
```

## 🐍 Python 직접 실행

### HTTP 모드
```bash
# 모듈로 실행
python -m dooray_mcp_server.main_http

# 설치된 패키지 명령어 사용 (pip install -e . 후)
dooray-mcp-server-http

# 커스텀 설정
python -m dooray_mcp_server.main_http --host 127.0.0.1 --port 8080
```

### STDIO 모드 (Claude Desktop 호환)
```bash
python -m dooray_mcp_server.main
dooray-mcp-server  # 설치 후
```

## 🐳 Docker 실행

### 이미지 빌드 및 실행
```bash
# 이미지 빌드
docker build -f Dockerfile.python -t dooray-mcp-python .

# HTTP 모드로 실행
docker run -p 8080:8080 \
  -e DOORAY_API_KEY="your_api_key" \
  -e DOORAY_BASE_URL="https://api.dooray.com" \
  dooray-mcp-python

# STDIO 모드로 실행 
docker run -i \
  -e DOORAY_API_KEY="your_api_key" \
  -e DOORAY_BASE_URL="https://api.dooray.com" \
  dooray-mcp-python dooray-mcp-server
```

### Docker Compose
```yaml
version: '3.8'
services:
  dooray-mcp:
    build:
      context: .
      dockerfile: Dockerfile.python
    ports:
      - "8080:8080"
    environment:
      - DOORAY_API_KEY=your_api_key
      - DOORAY_BASE_URL=https://api.dooray.com
      - DOORAY_LOG_LEVEL=INFO
    volumes:
      - ./.env:/app/.env:ro
```

## 🔧 개발 모드 실행

### 디버그 모드
```bash
export DOORAY_LOG_LEVEL=DEBUG
export DOORAY_HTTP_LOG_LEVEL=DEBUG
python -m dooray_mcp_server.main_http
```

### 개발 의존성과 함께
```bash
pip install -e ".[dev]"
python -m dooray_mcp_server.main_http --host 0.0.0.0
```

### 핫 리로드 (개발 시)
```bash
uvicorn dooray_mcp_server.transport.http_server_transport:app \
  --host 127.0.0.1 \
  --port 8080 \
  --reload
```

## 🖥️ Claude Desktop 설정 예제

### HTTP Transport 사용
```json
{
  "mcpServers": {
    "dooray-mcp-uvx": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/your-username/DoorayMCP",
        "dooray-mcp-server-http",
        "--port", "8080"
      ],
      "env": {
        "DOORAY_API_KEY": "your_api_key",
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
      "command": "python",
      "args": [
        "-m", "dooray_mcp_server.main_http",
        "--host", "127.0.0.1",
        "--port", "8080"
      ],
      "cwd": "/path/to/DoorayMCP",
      "env": {
        "DOORAY_API_KEY": "your_api_key",
        "DOORAY_BASE_URL": "https://api.dooray.com",
        "DOORAY_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### STDIO 모드 (기존 방식)
```json
{
  "mcpServers": {
    "dooray-mcp-stdio": {
      "command": "uvx",
      "args": [
        "--from", ".",
        "dooray-mcp-server"
      ],
      "env": {
        "DOORAY_API_KEY": "your_api_key",
        "DOORAY_BASE_URL": "https://api.dooray.com"
      }
    }
  }
}
```

## 🧪 테스트 및 검증

### 서버 상태 확인
```bash
# HTTP 모드 상태 확인
curl http://localhost:8080/health

# 응답 예시:
# {"status": "healthy", "server": "dooray-mcp-server"}
```

### MCP 프로토콜 테스트
```bash
# 도구 목록 조회
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

# Wiki 프로젝트 목록 조회 도구 실행
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
        "size": 5
      }
    }
  }'
```

### SSE 스트림 테스트
```bash
# Server-Sent Events 연결
curl -N -H "Accept: text/event-stream" http://localhost:8080/mcp
```

## 🎯 실제 사용 시나리오

### 1. 개발자 워크플로우
```bash
# 1. 프로젝트 클론
git clone https://github.com/your-username/DoorayMCP.git
cd DoorayMCP

# 2. 환경변수 설정
cp .env.example .env
# .env 파일 편집

# 3. uvx로 빠른 테스트
uvx --from . dooray-mcp-server-http --port 8080

# 4. 브라우저에서 http://localhost:8080/health 확인
```

### 2. 프로덕션 배포
```bash
# 1. Docker 이미지 빌드
docker build -f Dockerfile.python -t my-dooray-mcp:latest .

# 2. 프로덕션 실행
docker run -d \
  --name dooray-mcp \
  -p 8080:8080 \
  -e DOORAY_API_KEY="$DOORAY_API_KEY" \
  -e DOORAY_BASE_URL="$DOORAY_BASE_URL" \
  --restart unless-stopped \
  my-dooray-mcp:latest
```

### 3. CI/CD 파이프라인 테스트
```bash
# GitHub Actions에서
- name: Test MCP Server
  run: |
    uvx --from . dooray-mcp-server-http --port 8080 &
    sleep 5
    curl -f http://localhost:8080/health
```

## ⚠️ 주의사항

1. **환경변수**: 실제 API 키는 안전하게 관리
2. **포트 충돌**: 8080 포트가 사용 중이면 다른 포트 사용
3. **방화벽**: HTTP 모드 사용 시 포트 접근 권한 확인
4. **로그 레벨**: 프로덕션에서는 WARN 이상 권장

## 🔍 디버깅 팁

```bash
# 상세 로그 활성화
export DOORAY_LOG_LEVEL=DEBUG
export DOORAY_HTTP_LOG_LEVEL=DEBUG

# 특정 포트로 실행
uvx --from . dooray-mcp-server-http --port 8081

# 모든 인터페이스에 바인드 (주의: 보안상 위험)
uvx --from . dooray-mcp-server-http --host 0.0.0.0
```
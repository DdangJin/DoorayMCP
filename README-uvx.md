# Dooray MCP Server - uvx 실행 가이드

`uvx`를 사용하여 Dooray MCP 서버를 쉽게 실행할 수 있습니다.

## uvx란?

`uvx`는 Python 패키지를 격리된 환경에서 직접 실행할 수 있게 해주는 도구입니다. 별도의 가상환경 설정 없이 패키지를 바로 실행할 수 있습니다.

## 사전 요구사항

1. **uv 설치**:
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # 또는 Homebrew (macOS)
   brew install uv
   
   # 또는 pip
   pip install uv
   ```

2. **환경변수 설정**:
   ```bash
   export DOORAY_API_KEY="your_api_key_here"
   export DOORAY_BASE_URL="https://api.dooray.com"
   ```

## uvx 실행 방법

### 1. HTTP 모드 (Streamable HTTP Transport)

**기본 실행**:
```bash
uvx --from git+https://github.com/your-username/DoorayMCP dooray-mcp-server-http
```

**커스텀 설정**:
```bash
uvx --from git+https://github.com/your-username/DoorayMCP dooray-mcp-server-http \
  --host 0.0.0.0 --port 9000 --path /api/mcp
```

**로컬 소스에서 실행**:
```bash
# 현재 디렉토리에서
uvx --from . dooray-mcp-server-http

# 또는 절대 경로 지정
uvx --from /path/to/DoorayMCP dooray-mcp-server-http
```

### 2. STDIO 모드 (기존 Claude Desktop 호환)

```bash
uvx --from git+https://github.com/your-username/DoorayMCP dooray-mcp-server
```

**로컬 소스에서 실행**:
```bash
uvx --from . dooray-mcp-server
```

## 환경변수 파일 사용

`.env` 파일을 사용하려면:

```bash
# .env 파일 생성
cat > .env << EOF
DOORAY_API_KEY=your_api_key_here
DOORAY_BASE_URL=https://api.dooray.com
DOORAY_LOG_LEVEL=INFO
EOF

# .env 파일과 함께 실행
uvx --from . dooray-mcp-server-http --env-file .env
```

## Claude Desktop 설정 (uvx 사용)

`claude_desktop_config.json`에서 uvx를 사용하도록 설정:

```json
{
  "mcpServers": {
    "dooray-mcp-http": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/your-username/DoorayMCP",
        "dooray-mcp-server-http",
        "--host", "127.0.0.1",
        "--port", "8080"
      ],
      "env": {
        "DOORAY_API_KEY": "your_api_key_here",
        "DOORAY_BASE_URL": "https://api.dooray.com"
      }
    },
    "dooray-mcp-stdio": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/your-username/DoorayMCP",
        "dooray-mcp-server"
      ],
      "env": {
        "DOORAY_API_KEY": "your_api_key_here", 
        "DOORAY_BASE_URL": "https://api.dooray.com"
      }
    }
  }
}
```

## 로컬 개발용 설정

프로젝트를 클론한 후 로컬에서 개발하는 경우:

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
        "DOORAY_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

## 장점

1. **격리된 환경**: 시스템 Python 환경을 오염시키지 않음
2. **즉시 실행**: 가상환경 설정 불필요
3. **최신 버전**: Git에서 직접 최신 버전 실행 가능
4. **의존성 관리**: uv가 자동으로 의존성 해결
5. **빠른 속도**: uv의 빠른 패키지 설치

## 트러블슈팅

### 1. uv 설치 확인
```bash
uv --version
```

### 2. 환경변수 확인
```bash
echo $DOORAY_API_KEY
echo $DOORAY_BASE_URL
```

### 3. 실행 권한 확인
```bash
# 필요시 실행 권한 부여
chmod +x src/dooray_mcp_server/main_http.py
```

### 4. 로그 레벨 조정
```bash
export DOORAY_LOG_LEVEL=DEBUG
uvx --from . dooray-mcp-server-http
```

### 5. 포트 사용 중 오류
```bash
# 다른 포트 사용
uvx --from . dooray-mcp-server-http --port 8081
```

## 성능 팁

1. **캐시 활용**: uv는 패키지를 캐시하므로 두 번째 실행부터 더 빠름
2. **로컬 개발**: 빈번한 테스트 시 로컬 경로 사용
3. **환경변수**: `.env` 파일보다 시스템 환경변수가 더 빠름

## 추가 정보

- [uv 공식 문서](https://docs.astral.sh/uv/)
- [uvx 사용법](https://docs.astral.sh/uv/guides/tools/)
- [MCP 프로토콜](https://modelcontextprotocol.io/)
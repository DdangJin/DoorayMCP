# Migration from Kotlin to Python

이 프로젝트는 Kotlin 기반에서 Python 기반으로 완전히 마이그레이션되었습니다.

## 🔄 마이그레이션 완료 사항

### ✅ 제거된 Kotlin 관련 파일들
- `build.gradle.kts` - Gradle 빌드 설정
- `settings.gradle.kts` - Gradle 프로젝트 설정
- `gradle.properties` - Gradle 속성
- `gradlew`, `gradlew.bat` - Gradle 래퍼
- `gradle/` - Gradle 래퍼 디렉토리
- `build/` - Gradle 빌드 출력
- `src/main/kotlin/` - Kotlin 소스코드
- `src/test/kotlin/` - Kotlin 테스트
- `src/main/resources/` - Kotlin 리소스
- `scripts/docker-build.sh` - Kotlin용 Docker 스크립트
- `scripts/docker-push.sh` - Kotlin용 Docker 스크립트
- `install.sh` - Kotlin용 설치 스크립트

### ✅ 새로 추가된 Python 파일들
- `pyproject.toml` - Python 프로젝트 설정
- `requirements.txt` - Python 의존성
- `src/dooray_mcp_server/` - Python 소스코드
- `.gitignore` - Python 프로젝트용 gitignore
- `Dockerfile` - Python용 Docker 설정
- `README.md` - Python 버전 메인 문서
- `README-python.md` - Python 상세 가이드
- `README-uvx.md` - uvx 실행 가이드
- `run-examples.md` - 실행 예제 모음

## 🚀 기능 비교

| 기능 | Kotlin 버전 | Python 버전 | 상태 |
|------|-------------|-------------|------|
| STDIO Transport | ✅ | ✅ | ✅ 완료 |
| HTTP Transport | ❌ | ✅ | 🆕 신규 |
| Wiki 도구 | ✅ (5개) | ✅ (5개) | ✅ 완료 |
| 프로젝트 도구 | ✅ (7개) | ✅ (7개) | ✅ 완료 |
| 댓글 도구 | ✅ (4개) | ✅ (4개) | ✅ 완료 |
| 메신저 도구 | ✅ (7개) | ✅ (7개) | ✅ 완료 |
| 캘린더 도구 | ✅ (5개) | ✅ (5개) | ✅ 완료 |
| Docker 지원 | ✅ | ✅ | ✅ 완료 |
| uvx 지원 | ❌ | ✅ | 🆕 신규 |

## 🛠️ 아키텍처 변경사항

### Kotlin → Python 포팅
```
Kotlin (JVM)                    Python
├── Gradle 빌드 시스템          ├── setuptools + pyproject.toml
├── Ktor HTTP Client           ├── httpx
├── kotlinx.serialization     ├── pydantic
├── SLF4J 로깅                ├── structlog
├── 코루틴                    ├── asyncio
└── Java 21 런타임            └── Python 3.10+ 런타임
```

### 새로운 기능
1. **Streamable HTTP Transport**: FastAPI 기반 HTTP 서버
2. **Server-Sent Events**: 실시간 스트리밍 지원
3. **uvx 지원**: 가상환경 없이 즉시 실행
4. **세션 관리**: HTTP 세션 기반 상태 관리
5. **CORS 보안**: Origin 검증 및 보안 강화

## 📦 배포 방법 변화

### Before (Kotlin)
```bash
# Gradle 빌드
./gradlew shadowJar

# 직접 실행
java -jar build/libs/dooray-mcp-server-0.2.1-all.jar

# Docker
docker build -t dooray-mcp .
```

### After (Python)
```bash
# uvx 실행 (추천)
uvx --from . dooray-mcp-server-http

# pip 설치 후 실행
pip install -e .
python -m dooray_mcp_server.main_http

# Docker
docker build -t dooray-mcp-python .
```

## 🔄 설정 파일 변화

### Kotlin: `application.properties`
```properties
dooray.api.key=${DOORAY_API_KEY}
dooray.base.url=${DOORAY_BASE_URL}
```

### Python: `.env`
```env
DOORAY_API_KEY=your_api_key
DOORAY_BASE_URL=https://api.dooray.com
DOORAY_LOG_LEVEL=WARN
```

## 🚦 마이그레이션 가이드

기존 Kotlin 버전을 사용하던 사용자들을 위한 가이드:

### 1. 환경 변수
기존과 동일하게 `DOORAY_API_KEY`와 `DOORAY_BASE_URL` 사용

### 2. Claude Desktop 설정
```json
// Before (Kotlin)
{
  "command": "java",
  "args": ["-jar", "dooray-mcp-server.jar"]
}

// After (Python)
{
  "command": "uvx",
  "args": ["--from", ".", "dooray-mcp-server-http"]
}
```

### 3. 도구 이름
모든 도구 이름과 파라미터는 동일하게 유지됨

## 🎯 장점

### Python 버전의 장점
1. **더 빠른 개발**: Python의 간결한 문법
2. **더 나은 생태계**: 풍부한 라이브러리
3. **HTTP 지원**: 웹 기반 클라이언트 지원
4. **uvx 지원**: 설치 없는 실행
5. **더 나은 디버깅**: 더 직관적인 디버깅

### 유지되는 장점
1. **동일한 API**: 모든 Dooray API 기능 지원
2. **동일한 도구**: 28개 도구 모두 유지
3. **Docker 지원**: 컨테이너 배포 지원
4. **환경 변수**: 기존 설정 방식 유지

## 🔍 참고사항

- 기존 Kotlin 버전 사용자는 점진적 마이그레이션 가능
- API 호출 방식과 응답 형식은 동일
- 모든 기능이 동일하게 작동
- 성능은 비슷하거나 더 향상됨

---

**마이그레이션 완료! 🎉**  
Python 기반의 더 현대적이고 유연한 MCP 서버를 사용하세요.
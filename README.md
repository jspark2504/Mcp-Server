# Mcp Server

MCP(Model Context Protocol) 기반 **코딩 컨벤션 / 아키텍처 규칙 점검 서버**입니다.  
다른 Git 프로젝트(로컬 경로 또는 Git URL)를 입력하면, 구조/의존성/보안/테스트/아키텍처 규칙을 MCP **도구(tools)** 로 점검할 수 있습니다.

## 구조

- **`server.py`**  
  FastMCP 인스턴스와 `@mcp.tool()` 로 등록된 도구 정의
  - `analyze_structure(local_path?, git_url?)` — 레이어 디렉터리(`controller/service/repository`) 등 프로젝트 구조 점검
  - `check_dependencies(local_path?, git_url?, forbidden_libs?)` — `lombok` 등 금지 라이브러리 사용 여부 점검
  - `scan_secrets(local_path?, git_url?)` — `.env`, API 키/토큰 패턴 등 비밀정보 후보 탐지
  - `check_tests(local_path?, git_url?)` — `test`/`tests` 디렉터리 존재 등 테스트 구조 점검
  - `check_api_conventions(local_path?, git_url?)` — Controller 응답 래퍼 사용 여부 등 API 규칙 점검
  - `check_architecture_boundaries(local_path?, git_url?)` — Controller → Repository 직접 의존 같은 아키텍처 경계 위반 후보 탐지

- **`convention_checker/core.py`**  
  위 도구들이 사용하는 실제 검사 로직 모음 (git clone, 파일 순회, 규칙 체크 등).

## 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# (선택) .env 설정
cp .env.example .env

# MCP 서버 실행 (HTTP — 0.0.0.0:8000)
python server.py
# 또는
python app/main.py
```

## Cursor에서 사용

1. **Cursor Settings → MCP** 에서 서버 추가
2. 설정 예시 (로컬 HTTP):

```json
{
  "mcpServers": {
    "convention-checker": {
      "command": "C:/Users/parkj/anaconda3/python.exe",
      "args": ["C:/Users/parkj/Documents/GitHub/Mcp-Server/server.py"],
      "cwd": "C:/Users/parkj/Documents/GitHub/Mcp-Server"
    }
  }
}
```

3. 채팅/에이전트에서 다음과 같이 호출
   - **구조 점검**: `analyze_structure` 에 `local_path` 또는 `git_url` 전달  
   - **금지 라이브러리 점검**: `check_dependencies` 에 `forbidden_libs`(예: `["lombok"]`) 전달  
   - **비밀키 스캔**: `scan_secrets` 호출  
   - **테스트/아키텍처 규칙 점검**: `check_tests`, `check_api_conventions`, `check_architecture_boundaries` 호출


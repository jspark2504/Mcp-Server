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

---

## Python / Java 분석 툴 개요

- **서버 엔트리 (`server.py`)**
  - `FastMCP("convention-checker")` 기반 MCP 서버.
  - 각 `@mcp.tool()` 함수는 실제 로직을 `convention_checker.core` 또는 `tools.*` 모듈로 위임.

## 공통 분석 흐름 (Python / Java)

1. **프로젝트 로딩**  
   `load_project(path)` → 루트 경로·Git 여부 등 기본 정보 생성.

2. **파일 스캔**  
   - Python: `scan_python_files(project)` → `.py` 파일 전체 수집.  
   - Java: `scan_java_files(project)` → `.java` 파일 전체 수집.

3. **룰 실행**  
   `run_rules(files, rules)`  
   - 파일 내용/AST/임포트/클래스·메서드 정보 등을 준비한 뒤,  
   - 룰 이름에 맞는 함수(`*_rule`)들을 순서대로 호출 → `RuleResult` 리스트 반환.

## Python 전용 툴 (`analyze_python`)

- **대상**: Python 프로젝트 전체.
- **언어 규칙**
  - `pep8_variable_naming_rule`: 변수 이름 snake_case 여부.
  - `pep8_line_length_rule`: 한 줄 길이 120자 초과 여부.
- **레이어드 아키텍처**
  - `python_layered_router_repository_rule`: router → repository 직접 의존 금지.
  - `python_layered_router_service_rule`: router 는 service 레이어에 의존해야 함.
  - `python_layered_service_repository_rule`: service ↔ router/controller 역의존 금지.
  - `python_layered_package_structure_rule`: router/controller 파일이 repository·service 패키지 하위에 있지 않은지(패키지 구조) 검사.
- **FastAPI 규칙**
  - `fastapi_router_rule`: 라우터 파일이 FastAPI 라우터를 import 했는지.
  - `fastapi_dependency_rule`: 라우터 파일이 fastapi 모듈을 사용/의존하는지.
  - `fastapi_request_response_schema_rule`: 스키마/모델 파일에서 Request·Response·Schema 네이밍 분리 여부 검사.

## Java 전용 툴 (`analyze_java`)

- **대상**: Java/Spring 기반 프로젝트 전체.
- **언어 규칙**
  - `java_class_naming_rule`: 클래스 이름 PascalCase 여부.
  - `java_method_naming_rule`: 메서드 이름 camelCase 여부.
- **레이어드 아키텍처 / Service 규칙**
  - `java_layered_controller_repository_rule`: controller → repository 직접 의존 금지.
  - `java_layered_controller_service_rule`: controller 는 service 레이어에 의존해야 함.
  - `java_layered_service_repository_rule`: service ↔ controller 역의존 금지.
  - `java_service_transaction_rule`: service 레이어에서 데이터 변경 시 @Transactional 경계 설정 여부.
  - `java_service_constructor_injection_rule`: service 에서 필드 주입(@Autowired) 대신 생성자 주입 사용 여부.
  - `java_service_return_dto_rule`: service 가 영속 엔티티를 직접 노출하지 않고 DTO/응답 타입을 사용하는지 여부.
- **DTO 규칙**
  - `java_dto_request_response_separation_rule`: DTO 파일에서 *Request / *Response 클래스가 명확히 구분되어 있는지 여부.
- **Spring 규칙**
  - `spring_controller_annotation_rule`: controller 에 `@RestController` / `@Controller` 사용 여부.
  - `spring_controller_response_wrapper_rule`: controller 가 `ResponseEntity` 또는 공통 `ApiResponse` 등 응답 래퍼를 사용하는지 여부.
  - `spring_service_annotation_rule`: service 에 `@Service` 사용 여부.
  - `spring_repository_annotation_rule`: repository 에 `@Repository` 사용 여부.

## 요약

- Python/Java 각각: **프로젝트 로딩 → 파일 스캔 → 룰 실행 → 규약 위반 리스트(`RuleResult`) 반환.**
- 룰은 전부 `*_rule` 이름으로 통일되어 있고, **언어 스타일 / 레이어드 아키텍처 / 프레임워크 사용 규칙** 세 축을 중심으로 점검합니다.


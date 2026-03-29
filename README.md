# Mcp Server

MCP(Model Context Protocol) 기반 **코딩 컨벤션 / 아키텍처 규칙 점검 서버**입니다.  
다른 Git 프로젝트(로컬 경로 또는 Git URL)를 입력하면, 의존성·보안 점검과 Python/Java 규칙 분석 등을 MCP **도구(tools)** 로 호출할 수 있습니다.

## 구조

- **`server.py`** — `FastMCP` 인스턴스와 `@mcp.tool()` 로 노출되는 **MCP 도구** 정의.

| 순번 | 한글 레이블 | 도구 이름 (호출 시) | 인자·역할 요약 |
|:---:|:---|:---|:---|
| 1 | 생존 확인 | `ping()` | MCP 서버 응답 확인 |
| 2 | 금지 라이브러리 점검 | `check_dependencies(local_path?, git_url?, forbidden_libs?)` | 예: `lombok` 등 사용 여부 (`git clone` 지원) |
| 3 | 비밀정보 후보 탐지 | `scan_secrets(local_path?, git_url?)` | `.env`, API 키·토큰 패턴 등 |
| 4 | Python 규칙 상세 검사 | `analyze_python(path)` | PEP8·레이어·FastAPI 룰 전체 |
| 5 | Java 규칙 상세 검사 | `analyze_java(path)` | 네이밍·레이어·Spring·DTO 등 룰 전체 |
| 6 | README/docs ↔ 코드 요약 | `audit_project_vs_docs(project_path, language?, spec_glob?)` | `language`: `python`, `java`. 상세는 아래 해당 절·**4·5**번 도구 |
| 7 | check.md ↔ 코드 요약 | `audit_project_vs_check_spec(project_path, language?, spec_path?)` | 기본 `spec_path` = `check.md`. 단일 스펙 문서 기준 정합성 |

· **구현 모듈 (위 도구와 매핑)**

| 파일 | 담당 도구 번호 | 역할 |
|:---|:---:|:---|
| `convention_checker/core.py` | **2**, **3** | 로컬 또는 Git URL → clone·파일 순회·의존성·시크릿 검사 |
| `convention_checker/spec_audit.py` | **6**, **7** | 마크다운·코드 마커·룰 결과를 묶어 문서↔코드 **요약** 반환 |
| `tools/python/analyze_project.py`, `tools/java/analyze_project.py`, `engine/*`, `rules/*` | **4**, **5** | 언어별 파일 스캔·룰 실행 (`RuleResult` 목록) |

## 실행

```bash
pip install -r requirements.txt

# MCP stdio (Cursor / Claude Desktop 등에서 subprocess 로 붙을 때 — 기본)
python server.py

# MCP over HTTP (클라이언트가 HTTP MCP 를 지원할 때)
python app/main.py
```

`.env` 는 기본 동작에 필요하지 않습니다. 필요 시 `.env.example` 을 참고해 추가하면 됩니다.

## Cursor에서 사용

1. **Cursor Settings → MCP** 에서 서버 추가
2. 설정 예시 (**stdio** — `python server.py` 가 표준 입출력으로 MCP 를 처리):

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

3. 채팅/에이전트에서 예시
   - **금지 라이브러리 점검**: `check_dependencies` 에 `local_path` 또는 `git_url`, 필요 시 `forbidden_libs`(예: `["lombok"]`) 전달  
   - **비밀키 스캔**: `scan_secrets` 에 `local_path` 또는 `git_url` 전달  
   - **Python/Java 규칙**: `analyze_python` / `analyze_java` 에 프로젝트 루트 경로 전달  
   - **문서 대조 요약**: `audit_project_vs_docs` 호출
   - **check.md 기준 요약**: `audit_project_vs_check_spec(project_path, language, spec_path?)` 호출

## Claude에서 사용

**Claude Desktop**도 Cursor 와 같이 `mcpServers` 에 `command` / `args` / `cwd` 로 서버 프로세스를 띄웁니다. **위 Cursor 절의 JSON 과 동일**하게 넣으면 됩니다(`python`/`paths` 만 본인 환경에 맞게 수정).

1. 설정 파일 열기  
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
2. `mcpServers` 에 `convention-checker` 항목 추가(기존 서버가 있으면 **병합**).
3. 저장 후 **Claude Desktop 재시작** → 대화에서 MCP 도구 연결 확인.

**참고**: 웹 브라우저의 Claude(chat)만으로는 로컬 MCP 를 붙이지 못합니다. HTTP MCP 는 `app/main.py` + 클라이언트의 SSE/HTTP 지원 여부에 따릅니다.

---

## 공통 분석 흐름 (Python / Java) — 도구 **4**·**5**

`analyze_python` / `analyze_java` 안에서 아래 순서로 동작합니다.

| 단계 | 한글 | 함수·산출 |
|:---:|:---|:---|
| 1 | 프로젝트 로딩 | `load_project(path)` → 루트 경로·메타 정보 |
| 2 | 파일 스캔 | Python: `scan_python_files(project)` → `.py` 전부 / Java: `scan_java_files(project)` → `.java` 전부 |
| 3 | 룰 실행 | `run_rules(files, rules)` → 내용·AST·임포트 등 준비 후 `*_rule` 순서 호출 → **`RuleResult` 목록** |

감사 도구 **6**·**7**은 내부에서 같은 분석(`analyze_*_project`)을 불러 요약만 짧게 돌려줍니다.

## 문서 ↔ 코드 감사 — 도구 **6**·**7**

**공통**: MCP 응답을 짧게 두기 위해 **위반 목록·파일 경로·긴 제안 문장은 넣지 않습니다.** 상세는 같은 `project_path`로 **도구 4** 또는 **5**를 호출하세요.

### 6. README/docs ↔ 코드 (`audit_project_vs_docs`)

| 항목 | 내용 |
|:---|:---|
| 한글 레이블 | README·docs 기준 요약 감사 |
| 읽는 문서 | `README.md`(대소문자 변형 중 하나) + `docs/**/*.md` + (선택) `spec_glob` |
| 인자 | `project_path`(필수), `language`(`python`, `java`, 기본 `python`), `spec_glob`(선택) |
| 지원 언어 | `python`, `java`만. 그 외는 `unsupported_language` |

**반환 필드**

| 필드 | 한글 |
|:---|:---|
| `situation` | 판정 코드(아래 표) |
| `summary` | 한 줄 요약 |
| `violations` | 룰 위반 건수 |
| `doc_files` | 읽은 Markdown 개수 |
| `drift` | 문서에 없는 스택으로 추정될 때 코드 쪽 힌트(쉼표 문자열) 또는 `null` |
| `language` | 적용 언어 |

**`situation` (6번)**

| 값 | 한글 |
|:---|:---|
| `aligned` | 일치 |
| `spec_insufficient` | 문서 부족(md 없음 또는 본문 합계 약 250자 미만) |
| `mismatch` | 불일치(룰 위반 또는 문서 신호 vs 코드 마커 휴리스틱 불일치) |
| `unsupported_language` | 지원하지 않는 `language` |

**`drift` 예시 코드**(값 일부): Python — `undocumented_fastapi`, `undocumented_pydantic`, `undocumented_pytest` / Java — `undocumented_spring`, `undocumented_jpa`, `undocumented_junit`, `undocumented_lombok` 등.

### 7. check.md ↔ 코드 (`audit_project_vs_check_spec`)

| 항목 | 내용 |
|:---|:---|
| 한글 레이블 | 단일 스펙 파일 기준 요약 감사 |
| 읽는 문서 | 프로젝트 루트의 한 파일(기본 `check.md`, `spec_path`로 변경 가능) |
| 인자 | `project_path`, `language`, `spec_path`(선택, 기본 `check.md`) |
| 추가 반환 | `spec_file` — 실제로 읽은 스펙 파일 경로 |

**`situation` (7번)** — 6번 값에 더해 **`spec_not_found`**(해당 경로에 파일 없음). 나머지 `spec_insufficient` / `mismatch` / `aligned` / `unsupported_language` 의미는 6번과 같습니다.

## `check.md` 템플릿

이 저장소 루트의 `check.md`가 예시입니다. 점검 대상 프로젝트에도 두고 **도구 7**로 호출하면 됩니다.

## Python 룰 목록 — 도구 **`analyze_python` (4)**

**대상**: Python 프로젝트 루트.

| 구분 | 한글 | 룰 이름 |
|:---|:---|:---|
| 스타일 | 변수 snake_case | `pep8_variable_naming_rule` |
| 스타일 | 한 줄 120자 초과 | `pep8_line_length_rule` |
| 레이어 | router → repository 직접 금지 | `python_layered_router_repository_rule` |
| 레이어 | router는 service에 의존 | `python_layered_router_service_rule` |
| 레이어 | service ↔ router/controller 역의존 금지 | `python_layered_service_repository_rule` |
| 레이어 | 패키지 구조(router/controller가 repo·service 하위에 있지 않은지) | `python_layered_package_structure_rule` |
| FastAPI | 라우터가 FastAPI 라우터 import | `fastapi_router_rule` |
| FastAPI | fastapi 모듈 사용·의존 | `fastapi_dependency_rule` |
| FastAPI | Request/Response/Schema 네이밍 분리 | `fastapi_request_response_schema_rule` |

## Java 룰 목록 — 도구 **`analyze_java` (5)**

**대상**: Java/Spring 프로젝트 루트.

| 구분 | 한글 | 룰 이름 |
|:---|:---|:---|
| 스타일 | 클래스 PascalCase | `java_class_naming_rule` |
| 스타일 | 메서드 camelCase | `java_method_naming_rule` |
| 레이어 | controller → repository 직접 금지 | `java_layered_controller_repository_rule` |
| 레이어 | controller는 service에 의존 | `java_layered_controller_service_rule` |
| 레이어 | service ↔ controller 역의존 금지 | `java_layered_service_repository_rule` |
| Service | 데이터 변경 시 `@Transactional` | `java_service_transaction_rule` |
| Service | 생성자 주입(필드 `@Autowired` 지양) | `java_service_constructor_injection_rule` |
| Service | 엔티티 직접 반환 지양·DTO 등 | `java_service_return_dto_rule` |
| DTO | Request/Response 구분 | `java_dto_request_response_separation_rule` |
| Spring | `@RestController` / `@Controller` | `spring_controller_annotation_rule` |
| Spring | `ResponseEntity` / 공통 `ApiResponse` 등 | `spring_controller_response_wrapper_rule` |
| Spring | `@Service` | `spring_service_annotation_rule` |
| Spring | `@Repository` | `spring_repository_annotation_rule` |

## 한 줄 요약

**4**·**5**: 로드 → 스캔 → `*_rule` 실행 → `RuleResult` 리스트.**6**·**7**: 문서 + 같은 분석을 묶어 **짧은 요약**만 반환.


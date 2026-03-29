"""MCP 서버 진입점. `FastMCP`와 `@mcp.tool()` 정의, 분석 로직은 `convention_checker`·`tools`에 위임."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from convention_checker import core
from convention_checker import spec_audit
from tools.python.analyze_project import analyze_python_project
from tools.java.analyze_project import analyze_java_project


mcp = FastMCP("convention-checker")


@mcp.tool()
def ping() -> str:
    """MCP 서버 생존 확인용. 'pongs MCP' 반환."""
    return "pongs MCP"


@mcp.tool()
def check_dependencies(
    local_path: Optional[str] = None,
    git_url: Optional[str] = None,
    forbidden_libs: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """금지 라이브러리(lombok 등) 사용 여부를 검사합니다."""
    return core.check_dependencies(local_path=local_path, git_url=git_url, forbidden_libs=forbidden_libs)


@mcp.tool()
def scan_secrets(local_path: Optional[str] = None, git_url: Optional[str] = None) -> Dict[str, Any]:
    """보안/비밀키(.env, 토큰 패턴 등)를 간단히 탐지합니다."""
    return core.scan_secrets(local_path=local_path, git_url=git_url)


@mcp.tool()
def analyze_python(path: str):
    """Python 프로젝트 경로를 받아 컨벤션 룰(PEP8/레이어/FastAPI) 검사 후 결과 반환."""
    return analyze_python_project(path)


@mcp.tool()
def audit_project_vs_docs(
    project_path: str,
    language: str = "python",
    spec_glob: Optional[str] = None,
) -> Dict[str, Any]:
    """README/docs와 코드 대조 감사. language: python|java. 반환 요약 필드 — 상세는 README `audit_project_vs_docs` 절."""
    return spec_audit.audit_project_vs_docs(
        project_path, language=language, spec_glob=spec_glob
    )


@mcp.tool()
def audit_project_vs_check_spec(
    project_path: str,
    language: str = "python",
    spec_path: str = "check.md",
) -> Dict[str, Any]:
    """check.md(또는 지정 spec_path) 기준으로 코드 정합성 요약 감사."""
    return spec_audit.audit_project_vs_check_spec(
        project_path, language=language, spec_path=spec_path
    )


@mcp.tool()
def analyze_java(path: str):
    """Java 프로젝트 경로를 받아 컨벤션 룰(네이밍/레이어/Spring/DTO) 검사 후 결과 반환."""
    return analyze_java_project(path)

if __name__ == "__main__":
    mcp.run()
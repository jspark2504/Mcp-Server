"""
MCP 서버 진입점이자 MCP 툴 정의 파일.

이미지 예시처럼 `FastMCP` + `@mcp.tool()` 이 여기 다 모여 있고,
실제 검사 로직은 `convention_checker.core` 에서 import 해서 사용합니다.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from convention_checker import core
from convention_checker import spec_audit
from tools.python.analyze_project import analyze_python_project
from tools.java.analyze_project import analyze_java_project
import sys

from datetime import datetime


mcp = FastMCP("convention-checker")
print("THIS SERVER LOADED")


@mcp.tool()
def ping() -> str:
    """MCP 서버 생존 확인용. 'pongs MCP' 반환."""
    return "pongs MCP"


@mcp.tool()
def analyze_structure(local_path: Optional[str] = None, git_url: Optional[str] = None) -> Dict[str, Any]:
    """프로젝트 구조(레이어 디렉터리 등)를 검사합니다."""
    return core.analyze_structure(local_path=local_path, git_url=git_url)


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
def check_tests(local_path: Optional[str] = None, git_url: Optional[str] = None) -> Dict[str, Any]:
    """테스트 디렉터리 존재 여부 등을 확인합니다."""
    return core.check_tests(local_path=local_path, git_url=git_url)


@mcp.tool()
def check_api_conventions(local_path: Optional[str] = None, git_url: Optional[str] = None) -> Dict[str, Any]:
    """Controller 응답 방식 등 API 관련 규칙을 간단히 점검합니다."""
    return core.check_api_conventions(local_path=local_path, git_url=git_url)


@mcp.tool()
def check_architecture_boundaries(local_path: Optional[str] = None, git_url: Optional[str] = None) -> Dict[str, Any]:
    """Controller → Repository 직접 의존 같은 아키텍처 경계 위반 후보를 탐지합니다."""
    return core.check_architecture_boundaries(local_path=local_path, git_url=git_url)

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
def analyze_java(path: str):
    """Java 프로젝트 경로를 받아 컨벤션 룰(네이밍/레이어/Spring/DTO) 검사 후 결과 반환."""
    return analyze_java_project(path)

if __name__ == "__main__":
    mcp.run()
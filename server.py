"""
MCP 서버 진입점이자 MCP 툴 정의 파일.

이미지 예시처럼 `FastMCP` + `@mcp.tool()` 이 여기 다 모여 있고,
실제 검사 로직은 `convention_checker.core` 에서 import 해서 사용합니다.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from convention_checker import core

import sys

from datetime import datetime


mcp = FastMCP("convention-checker")
print("THIS SERVER LOADED")


@mcp.tool()
def ping() -> str:
    return "pongs"

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


if __name__ == "__main__":
    mcp.run()
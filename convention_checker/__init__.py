"""
코딩 컨벤션 검사용 순수 로직 패키지.

MCP 관련 코드는 `server.py` 에 있고,
여기서는 검사 함수들만 노출합니다.
"""

from .core import (
    check_dependencies,
    scan_secrets,
)

__all__ = [
    "check_dependencies",
    "scan_secrets",
]

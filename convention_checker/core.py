"""의존성·비밀정보 등 저장소 단위 경량 검사(재사용 가능). 언어별 룰은 `tools`·`engine`에서 실행."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional


def clone_if_needed(local_path: Optional[str], git_url: Optional[str]) -> Path:
    """
    local_path 또는 git_url 중 하나를 받아 실제 검사 대상 루트 경로를 반환합니다.
    git_url 이면 임시 디렉터리에 clone 합니다.
    """
    if not local_path and not git_url:
        raise ValueError("local_path 나 git_url 중 하나는 반드시 지정해야 합니다.")

    if local_path:
        root = Path(local_path).expanduser().resolve()
        if not root.exists():
            raise FileNotFoundError(f"경로를 찾을 수 없습니다: {root}")
        return root

    # git_url 이 주어진 경우
    tmp_dir = Path(tempfile.mkdtemp(prefix="mcp-conv-"))
    subprocess.run(["git", "clone", "--depth", "1", git_url, str(tmp_dir)], check=True)
    return tmp_dir


def safe_cleanup(path: Path, base_tmp_prefix: str = "mcp-conv-") -> None:
    """우리가 만든 임시 clone 디렉터리인 경우에만 정리합니다."""
    try:
        if path.name.startswith(base_tmp_prefix) and path.exists():
            shutil.rmtree(path, ignore_errors=True)
    except Exception:
        # 정리는 실패해도 검사 결과에는 영향을 주지 않도록 무시
        pass


def walk_files(root: Path) -> List[Path]:
    """루트 이하의 파일 경로를 전부 나열합니다(.git 등은 제외)."""
    files: List[Path] = []
    for dirpath, _, filenames in os.walk(root):
        # .git 등의 디렉터리는 스킵
        if ".git" in dirpath.split(os.sep):
            continue
        for name in filenames:
            files.append(Path(dirpath) / name)
    return files


def check_dependencies(
    local_path: Optional[str] = None,
    git_url: Optional[str] = None,
    forbidden_libs: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    금지 의존성/라이브러리 사용 여부를 검사합니다.

    - 기본 금지 목록: lombok
    - Gradle/Maven/requirements.txt 등을 간단히 문자열 검색으로 확인
    """
    if forbidden_libs is None:
        forbidden_libs = ["lombok"]

    root = clone_if_needed(local_path, git_url)
    is_tmp = git_url is not None and local_path is None

    try:
        files = walk_files(root)
        violations: Dict[str, List[str]] = {lib: [] for lib in forbidden_libs}

        for f in files:
            if not f.suffix.lower() in {".gradle", ".kts", ".xml", ".java", ".kt", ".txt", ".md", ".py"}:
                continue
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for lib in forbidden_libs:
                if lib in text:
                    violations.setdefault(lib, []).append(str(f.relative_to(root)))

        return {
            "root": str(root),
            "forbidden_libs": forbidden_libs,
            "violations": violations,
        }
    finally:
        if is_tmp:
            safe_cleanup(root)


def scan_secrets(local_path: Optional[str] = None, git_url: Optional[str] = None) -> Dict[str, Any]:
    """
    보안/비밀키를 간단히 탐지합니다.

    - .env / .env.* 파일 존재 여부
    - API 키/토큰 패턴 (예: sk-*, AKIA*, xoxb-* 등) 문자열 검색
    """
    root = clone_if_needed(local_path, git_url)
    is_tmp = git_url is not None and local_path is None

    try:
        files = walk_files(root)
        env_files: List[str] = []
        suspected: List[Dict[str, Any]] = []

        secret_patterns = [
            re.compile(r"sk-[A-Za-z0-9]{20,}"),
            re.compile(r"AKIA[0-9A-Z]{16}"),
            re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
            re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\\\"][A-Za-z0-9\\-_=]{16,}"),
        ]

        for f in files:
            rel = str(f.relative_to(root))
            name = f.name

            if name.startswith(".env"):
                env_files.append(rel)

            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            for pattern in secret_patterns:
                for m in pattern.finditer(text):
                    snippet = m.group(0)
                    suspected.append(
                        {
                            "file": rel,
                            "match": snippet[:60] + ("..." if len(snippet) > 60 else ""),
                        }
                    )

        return {
            "root": str(root),
            "env_files": env_files,
            "suspected_secrets": suspected,
        }
    finally:
        if is_tmp:
            safe_cleanup(root)


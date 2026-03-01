"""
코딩 컨벤션 / 아키텍처 규칙 점검용 순수 로직 모듈.

MCP와 직접 연결되지 않은, 재사용 가능한 검사 함수들을 모아둡니다.
"""

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


def analyze_structure(local_path: Optional[str] = None, git_url: Optional[str] = None) -> Dict[str, Any]:
    """
    프로젝트 구조를 검사합니다.

    - controller/service/repository 디렉터리 존재 여부
    - src/main/java, src/test/java 등 기본 구조 확인
    """
    root = clone_if_needed(local_path, git_url)
    is_tmp = git_url is not None and local_path is None

    try:
        layers = {
            "controller": False,
            "service": False,
            "repository": False,
        }
        layer_paths: Dict[str, List[str]] = {k: [] for k in layers}

        for dirpath, _, _ in os.walk(root):
            rel = os.path.relpath(dirpath, root)
            parts = rel.replace("\\", "/").split("/")
            for layer in layers.keys():
                if layer in parts:
                    layers[layer] = True
                    layer_paths[layer].append(rel)

        return {
            "root": str(root),
            "layers": layers,
            "layer_paths": layer_paths,
        }
    finally:
        if is_tmp:
            safe_cleanup(root)


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


def check_tests(local_path: Optional[str] = None, git_url: Optional[str] = None) -> Dict[str, Any]:
    """
    테스트/커버리지 관련 기본 정책을 확인합니다.

    - test / tests 디렉터리 존재 여부
    - src/test/java 같은 경로 존재 여부
    """
    root = clone_if_needed(local_path, git_url)
    is_tmp = git_url is not None and local_path is None

    try:
        has_test_dir = False
        test_dirs: List[str] = []

        for dirpath, _, _ in os.walk(root):
            rel = os.path.relpath(dirpath, root)
            parts = rel.replace("\\", "/").split("/")
            if any(p in {"test", "tests"} for p in parts):
                has_test_dir = True
                test_dirs.append(rel)

        return {
            "root": str(root),
            "has_test_dir": has_test_dir,
            "test_dirs": test_dirs,
        }
    finally:
        if is_tmp:
            safe_cleanup(root)


def check_api_conventions(local_path: Optional[str] = None, git_url: Optional[str] = None) -> Dict[str, Any]:
    """
    API(Controller) 관련 기본 규칙을 가볍게 확인합니다.

    - controller 디렉터리 내 파일에서 응답 래퍼/공통 Response 사용 여부 후보를 수집
      (예: ApiResponse, ResponseEntity 등 문자열 기반 탐지)
    """
    root = clone_if_needed(local_path, git_url)
    is_tmp = git_url is not None and local_path is None

    try:
        controller_files: List[str] = []
        possible_raw_responses: List[str] = []

        for f in walk_files(root):
            rel = str(f.relative_to(root))
            parts = rel.replace("\\", "/").split("/")
            if "controller" not in parts:
                continue
            controller_files.append(rel)

            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            # 아주 단순한 휴리스틱: 공통 래퍼가 아니라 primitive/도메인을 바로 반환하는 패턴 후보
            if re.search(r"public\\s+[A-Z][A-Za-z0-9_<>]*\\s+\\w+\\(", text) and not (
                "ResponseEntity" in text or "ApiResponse" in text
            ):
                possible_raw_responses.append(rel)

        return {
            "root": str(root),
            "controller_files": controller_files,
            "possible_raw_responses": possible_raw_responses,
        }
    finally:
        if is_tmp:
            safe_cleanup(root)


def check_architecture_boundaries(
    local_path: Optional[str] = None, git_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    아키텍처 경계 규칙(예: controller가 repository 직접 호출 금지)을 간단히 검사합니다.

    - controller 디렉터리 내 파일에서 'Repository' 라는 단어가 등장하는지 탐지
      (정적 분석이 아닌 문자열 기반 후보 탐지 수준)
    """
    root = clone_if_needed(local_path, git_url)
    is_tmp = git_url is not None and local_path is None

    try:
        direct_repo_calls: List[str] = []

        for f in walk_files(root):
            rel = str(f.relative_to(root))
            parts = rel.replace("\\", "/").split("/")
            if "controller" not in parts:
                continue

            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            if "Repository" in text:
                direct_repo_calls.append(rel)

        return {
            "root": str(root),
            "controller_direct_repository_usages": direct_repo_calls,
        }
    finally:
        if is_tmp:
            safe_cleanup(root)


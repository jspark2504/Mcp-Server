"""
Markdown 스펙(문서)과 코드 분석 결과를 맞춰 보는 감사 로직.

Python / Java 프로젝트: 각각 `analyze_python_project` / `analyze_java_project` 결과를 사용합니다.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from models.result_model import RuleResult
from tools.java.analyze_project import analyze_java_project
from tools.python.analyze_project import analyze_python_project

SKIP_DIR_NAMES = {
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "node_modules",
    "dist",
    "build",
    ".mypy_cache",
    ".tox",
    "target",
    ".gradle",
    "site-packages",
}

# 문서에서 키워드 그룹 중 하나라도 보이면 해당 주제가 문서화된 것으로 간주
DOC_SIGNAL_GROUPS: Dict[str, Tuple[str, ...]] = {
    "fastapi": ("fastapi",),
    "pydantic": ("pydantic",),
    "testing": ("pytest", "unittest", "테스트", "test", "단위"),
    "style": ("pep 8", "pep8", "ruff", "black", "formatter", "lint", "checkstyle", "spotless"),
    "layered_architecture": ("layer", "레이어", "repository", "service", "router", "controller"),
    "spring": ("spring", "spring boot", "springboot"),
    "jpa": ("jpa", "hibernate", "jakarta.persistence", "javax.persistence"),
    "junit": ("junit", "mockito"),
    "lombok": ("lombok",),
}

CODE_MARKERS_PY: Dict[str, str] = {
    "fastapi": "fastapi",
    "pydantic": "pydantic",
    "pytest": "pytest",
    "flask": "flask",
    "django": "django",
}

# .java 본문(소문자)에 부분 문자열이 있으면 해당 스택/도구 사용으로 간주
CODE_MARKERS_JAVA: Dict[str, Tuple[str, ...]] = {
    "spring": ("org.springframework", "springframework"),
    "jpa": ("jakarta.persistence", "javax.persistence"),
    "junit": ("org.junit", "junit.jupiter", "junit.framework"),
    "mockito": ("org.mockito", "mockito"),
    "lombok": ("lombok",),
}

MIN_SPEC_CHARS = 250

SUPPORTED_LANGUAGES = frozenset({"python", "java"})


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _collect_default_markdown(root: Path) -> List[Tuple[str, str]]:
    """README·docs/**/*.md 를 수집합니다."""
    out: List[Tuple[str, str]] = []
    for name in ("README.md", "readme.md", "Readme.md"):
        p = root / name
        if p.is_file():
            out.append((str(p), _read_text(p)))
            break
    docs = root / "docs"
    if docs.is_dir():
        for p in sorted(docs.rglob("*.md")):
            if p.is_file():
                out.append((str(p), _read_text(p)))
    return out


def _collect_glob_markdown(root: Path, pattern: str) -> List[Tuple[str, str]]:
    """프로젝트 루트 기준 glob(예: docs/**/*.md)로 추가 수집."""
    out: List[Tuple[str, str]] = []
    try:
        for p in sorted(root.glob(pattern)):
            if p.is_file() and p.suffix.lower() == ".md":
                text = _read_text(p)
                if text:
                    out.append((str(p), text))
    except Exception:
        pass
    return out


def _merge_docs(
    base: List[Tuple[str, str]], extra: List[Tuple[str, str]]
) -> List[Tuple[str, str]]:
    seen = {path for path, _ in base}
    merged = list(base)
    for path, text in extra:
        if path not in seen:
            seen.add(path)
            merged.append((path, text))
    return merged


def _detect_doc_signals(md_lower: str) -> Dict[str, bool]:
    return {
        key: any(token in md_lower for token in tokens)
        for key, tokens in DOC_SIGNAL_GROUPS.items()
    }


def _scan_python_markers(root: Path) -> Dict[str, bool]:
    found = {k: False for k in CODE_MARKERS_PY}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            fp = Path(dirpath) / fn
            try:
                text = fp.read_text(encoding="utf-8", errors="ignore").lower()
            except OSError:
                continue
            for key, needle in CODE_MARKERS_PY.items():
                if needle in text:
                    found[key] = True
    return found


def _scan_java_markers(root: Path) -> Dict[str, bool]:
    found = {k: False for k in CODE_MARKERS_JAVA}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for fn in filenames:
            if not fn.endswith(".java"):
                continue
            fp = Path(dirpath) / fn
            try:
                text = fp.read_text(encoding="utf-8", errors="ignore").lower()
            except OSError:
                continue
            for key, needles in CODE_MARKERS_JAVA.items():
                if any(n in text for n in needles):
                    found[key] = True
    return found


def _top_rule_counts(results: List[RuleResult], limit: int = 3) -> str:
    by_rule: Dict[str, int] = {}
    for r in results:
        by_rule[r.rule_name] = by_rule.get(r.rule_name, 0) + 1
    top = sorted(by_rule.items(), key=lambda x: -x[1])[:limit]
    if not top:
        return "-"
    return ",".join(f"{n}:{c}" for n, c in top)


def _compute_drift_python(
    doc_signals: Dict[str, bool], code_markers: Dict[str, bool]
) -> List[str]:
    drift: List[str] = []
    if code_markers.get("fastapi") and not doc_signals.get("fastapi"):
        drift.append("undocumented_fastapi")
    if code_markers.get("pydantic") and not doc_signals.get("pydantic"):
        drift.append("undocumented_pydantic")
    if code_markers.get("pytest") and not doc_signals.get("testing"):
        drift.append("undocumented_pytest")
    return drift


def _compute_drift_java(
    doc_signals: Dict[str, bool], code_markers: Dict[str, bool]
) -> List[str]:
    drift: List[str] = []
    if code_markers.get("spring") and not doc_signals.get("spring"):
        drift.append("undocumented_spring")
    if code_markers.get("jpa") and not doc_signals.get("jpa"):
        drift.append("undocumented_jpa")
    if code_markers.get("junit") and not (
        doc_signals.get("junit") or doc_signals.get("testing")
    ):
        drift.append("undocumented_junit")
    if code_markers.get("mockito") and not (
        doc_signals.get("junit") or doc_signals.get("testing")
    ):
        drift.append("undocumented_mockito")
    if code_markers.get("lombok") and not doc_signals.get("lombok"):
        drift.append("undocumented_lombok")
    return drift


def _run_analysis(language: str, root: Path) -> List[RuleResult]:
    if language == "python":
        return analyze_python_project(str(root))
    return analyze_java_project(str(root))


def _detail_tool_name(language: str) -> str:
    return "analyze_python" if language == "python" else "analyze_java"


def audit_project_vs_docs(
    project_path: str,
    language: str = "python",
    spec_glob: Optional[str] = None,
) -> Dict[str, Any]:
    """
    프로젝트 루트의 Markdown 과 코드(Python 또는 Java)를 비교해 감사 결과를 반환합니다.

    반환 필드는 짧게 유지합니다. 상세는 README `audit_project_vs_docs` 절과
    `analyze_python` / `analyze_java` 툴을 참고하세요.
    """
    root = Path(project_path).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"프로젝트 경로가 디렉터리가 아니거나 없습니다: {root}")

    lang = (language or "python").strip().lower()
    if lang not in SUPPORTED_LANGUAGES:
        return {
            "situation": "unsupported_language",
            "summary": f"[미지원] language는 python|java 만 지원 · 요청={language!r}",
            "violations": 0,
            "doc_files": 0,
            "drift": None,
            "language": lang,
        }

    docs = _collect_default_markdown(root)
    if spec_glob:
        docs = _merge_docs(docs, _collect_glob_markdown(root, spec_glob))

    md_concat = "\n\n".join(t for _, t in docs)
    md_lower = md_concat.lower()
    total_chars = len(md_concat.strip())
    doc_signals = _detect_doc_signals(md_lower)

    if lang == "python":
        code_markers_combined: Dict[str, Any] = _scan_python_markers(root)
        drift_codes = _compute_drift_python(doc_signals, code_markers_combined)
    else:
        code_markers_combined = _scan_java_markers(root)
        drift_codes = _compute_drift_java(doc_signals, code_markers_combined)

    spec_insufficient_reason: Optional[str] = None
    if not docs:
        spec_insufficient_reason = "md 없음(README·docs)"
    elif total_chars < MIN_SPEC_CHARS:
        spec_insufficient_reason = f"짧음({total_chars}<{MIN_SPEC_CHARS}자)"

    rule_results = _run_analysis(lang, root)
    violation_count = len(rule_results)
    top_rules = _top_rule_counts(rule_results)

    drift_str = ",".join(drift_codes) if drift_codes else None
    doc_n = len(docs)
    detail_tool = _detail_tool_name(lang)

    if spec_insufficient_reason:
        situation = "spec_insufficient"
        summary = (
            f"[문서부족] md={doc_n}·{total_chars}자 · {spec_insufficient_reason}"
            + (f" · 위반={violation_count}" if violation_count else "")
        )
    elif violation_count > 0:
        situation = "mismatch"
        summary = (
            f"[불일치] 위반={violation_count} · 상위룰={top_rules} · md={doc_n} · 상세={detail_tool}"
        )
    elif drift_codes:
        situation = "mismatch"
        summary = f"[불일치] 문서미기재={drift_str} · md={doc_n} · README에 스택/테스트 명시"
    else:
        situation = "aligned"
        summary = f"[일치] md={doc_n} · 위반=0 · lang={lang} · (휴리스틱 기준)"

    return {
        "situation": situation,
        "summary": summary.strip(),
        "violations": violation_count,
        "doc_files": doc_n,
        "drift": drift_str,
        "language": lang,
    }

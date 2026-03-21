# 언어별 코드 파일 탐색
import os

# 소스 스캔 시 건너뛸 디렉터리 (가상환경·빌드 산출물 등)
_SKIP_WALK_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    ".mypy_cache",
    ".tox",
    "node_modules",
    "dist",
    "build",
    "site-packages",
    "target",
    ".gradle",
}


def scan_python_files(project):
    """project.root_path 기준 os.walk로 하위 .py 수집. venv/site-packages 등은 제외."""

    python_files = []

    for root, dirs, files in os.walk(project.root_path):
        dirs[:] = [d for d in dirs if d not in _SKIP_WALK_DIRS]

        for file in files:

            if file.endswith(".py"):

                full_path = os.path.join(root, file)

                python_files.append(full_path)

    return python_files


def scan_java_files(project):
    """project.root_path 기준 os.walk로 하위 .java 수집. target/.gradle 등은 제외."""

    java_files = []

    for root, dirs, files in os.walk(project.root_path):
        dirs[:] = [d for d in dirs if d not in _SKIP_WALK_DIRS]

        for file in files:

            if file.endswith(".java"):

                full_path = os.path.join(root, file)

                java_files.append(full_path)

    return java_files

def read_file(file_path):
    """파일 경로를 UTF-8로 읽어 문자열 반환. 실패 시 빈 문자열 반환."""

    try:

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    except Exception:
        return ""
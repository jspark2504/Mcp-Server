# 언어별 코드 파일 탐색
import os


def scan_python_files(project):
    """project.root_path 기준 os.walk로 하위 모든 .py 파일 경로 리스트 반환."""

    python_files = []

    for root, dirs, files in os.walk(project.root_path):

        for file in files:

            if file.endswith(".py"):

                full_path = os.path.join(root, file)

                python_files.append(full_path)

    return python_files


def scan_java_files(project):
    """project.root_path 기준 os.walk로 하위 모든 .java 파일 경로 리스트 반환."""

    java_files = []

    for root, dirs, files in os.walk(project.root_path):

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
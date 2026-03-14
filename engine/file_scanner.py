# 언어별 코드 파일 탐색
import os


def scan_python_files(project):

    python_files = []

    for root, dirs, files in os.walk(project.root_path):

        for file in files:

            if file.endswith(".py"):

                full_path = os.path.join(root, file)

                python_files.append(full_path)

    return python_files


def scan_java_files(project):

    java_files = []

    for root, dirs, files in os.walk(project.root_path):

        for file in files:

            if file.endswith(".java"):

                full_path = os.path.join(root, file)

                java_files.append(full_path)

    return java_files

def read_file(file_path):

    try:

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    except Exception:
        return ""
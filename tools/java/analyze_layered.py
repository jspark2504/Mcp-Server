from engine.project_loader import load_project
from engine.file_scanner import scan_java_files
from engine.rule_runner import run_rules


def analyze_java_layered(project_path: str):
    """
    Java 프로젝트의 Layered Architecture 검사
    controller → service → repository 구조 검증
    """

    # 1. 프로젝트 로딩
    project = load_project(project_path)

    # 2. Java 파일 스캔
    java_files = scan_java_files(project)

    # 3. 실행할 rule 정의
    rules = [
        "java_layered_controller_service_rule",
        "java_layered_service_repository_rule",
        "java_layered_controller_repository_violation"
    ]

    # 4. rule 실행
    results = run_rules(java_files, rules)

    return results
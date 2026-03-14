from engine.project_loader import load_project
from engine.file_scanner import scan_java_files
from engine.rule_runner import run_rules


def analyze_spring_architecture(project_path: str):
    """
    Spring Framework 기반 구조 검사
    """

    project = load_project(project_path)

    java_files = scan_java_files(project)

    rules = [
        "spring_controller_annotation_rule",
        "spring_service_annotation_rule",
        "spring_repository_annotation_rule"
    ]

    results = run_rules(java_files, rules)

    return results
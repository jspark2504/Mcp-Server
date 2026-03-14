from engine.project_loader import load_project
from engine.file_scanner import scan_python_files
from engine.rule_runner import run_rules


def analyze_python_layered(project_path: str):
    """
    Python Layered Architecture 검사
    """

    project = load_project(project_path)

    python_files = scan_python_files(project)

    rules = [
        "python_layered_router_service_rule",
        "python_layered_service_repository_rule",
        "python_layered_router_repository_violation"
    ]

    results = run_rules(python_files, rules)

    return results
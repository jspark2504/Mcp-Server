from engine.project_loader import load_project
from engine.file_scanner import scan_python_files
from engine.rule_runner import run_rules


def analyze_python_project(project_path: str):
    """프로젝트 루트 경로를 받아 .py 파일을 스캔한 뒤 정의된 Python 룰들을 실행해 위반 목록 반환."""

    project = load_project(project_path)

    python_files = scan_python_files(project)

    rules = [
        # language rules
        "pep8_variable_naming_rule",
        "pep8_line_length_rule",

        # architecture rules
        "python_layered_router_repository_rule",
        "python_layered_router_service_rule",
        "python_layered_service_repository_rule",
        "python_layered_package_structure_rule",

        # framework rules
        "fastapi_router_rule",
        "fastapi_dependency_rule",
        "fastapi_request_response_schema_rule",
    ]

    results = run_rules(python_files, rules)

    return results
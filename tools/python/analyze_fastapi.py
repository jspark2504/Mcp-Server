from engine.project_loader import load_project
from engine.file_scanner import scan_python_files
from engine.rule_runner import run_rules


def analyze_fastapi(project_path: str):
    """
    FastAPI 프로젝트 구조 분석
    """

    # 프로젝트 로딩
    project = load_project(project_path)

    # Python 파일 탐색
    python_files = scan_python_files(project)

    # 실행할 rule 목록
    rules = [
        "fastapi_router_rule",
        "fastapi_dependency_rule",
        "fastapi_response_model_rule"
    ]

    # rule 실행
    results = run_rules(python_files, rules)

    return results
from engine.project_loader import load_project
from engine.file_scanner import scan_java_files
from engine.rule_runner import run_rules


def analyze_java_project(project_path: str):
    """
    Java 프로젝트 전체 코드 분석
    """

    # 프로젝트 로딩
    project = load_project(project_path)

    # Java 파일 탐색
    java_files = scan_java_files(project)

    # 실행할 rule 목록
    rules = [
        # language rules
        "java_class_naming_rule",
        "java_method_naming_rule",

        # architecture / service rules
        "java_layered_controller_repository_rule",
        "java_layered_controller_service_rule",
        "java_layered_service_repository_rule",
        "java_service_transaction_rule",
        "java_service_constructor_injection_rule",
        "java_service_return_dto_rule",

        # DTO rules
        "java_dto_request_response_separation_rule",

        # framework rules
        "spring_controller_annotation_rule",
        "spring_controller_response_wrapper_rule",
        "spring_service_annotation_rule",
        "spring_repository_annotation_rule",
    ]

    results = run_rules(java_files, rules)

    return results
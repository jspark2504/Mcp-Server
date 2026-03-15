# rule 실행 및 결과 수집
import importlib
import re
from engine.file_scanner import read_file
from engine.ast_parser import parse_python_ast, extract_python_imports, extract_python_classes
from models.result_model import RuleResult


RULE_MODULES = [
    "rules.language.python.pep8_rules",
    "rules.language.java.naming_rules",
    "rules.architecture.layered.python_layered_rules",
    "rules.architecture.layered.java_layered_rules",
    "rules.dto.java_dto_rules",
    "rules.framework.fastapi_rules",
    "rules.framework.spring_rules",
]


def load_rule_function(rule_name):
    """RULE_MODULES 순회하며 rule_name과 같은 이름의 함수를 찾아 반환. 없으면 예외."""

    for module_path in RULE_MODULES:

        module = importlib.import_module(module_path)

        if hasattr(module, rule_name):

            return getattr(module, rule_name)

    raise Exception(f"Rule not found: {rule_name}")


def _extract_java_classes(content: str):
    """Java 소스 문자열에서 'class Foo' 패턴으로 클래스 이름만 추출해 리스트 반환."""

    classes = []
    for match in re.finditer(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)", content):
        classes.append(match.group(1))
    return classes


def _extract_java_methods(content: str):
    """Java 소스에서 메서드 선언 패턴으로 메서드 이름만 추출해 리스트 반환."""

    methods = []
    pattern = re.compile(
        r"\b(?:public|protected|private)?\s*(?:static\s+)?"
        r"[A-Za-z0-9_<>\[\],\s]+\s+([a-zA-Z_][A-Za-z0-9_]*)\s*\(",
    )
    for match in pattern.finditer(content):
        methods.append(match.group(1))
    return methods


def run_rules(files, rule_names):
    """각 파일에 대해 내용/AST/imports 등 파싱 후 rule_names 순서대로 룰 실행해 RuleResult 리스트 반환."""

    results = []

    for file_path in files:

        content = read_file(file_path)

        if not content:
            continue

        lines = content.split("\n")

        tree = None
        imports = []
        python_classes = []
        java_classes = []
        java_methods = []

        # python AST 파싱
        if file_path.endswith(".py"):

            tree = parse_python_ast(content)

            if tree:
                imports = extract_python_imports(tree)
                python_classes = extract_python_classes(tree)

        # java 단순 파싱
        if file_path.endswith(".java"):
            java_classes = _extract_java_classes(content)
            java_methods = _extract_java_methods(content)

        # rule 실행
        for rule_name in rule_names:

            rule_func = load_rule_function(rule_name)

            try:

                rule_results = []

                # rule별 인자 처리
                if "pep8_line_length_rule" == rule_name:

                    rule_results = rule_func(file_path, lines)

                elif "pep8_variable_naming_rule" == rule_name:

                    if tree:
                        rule_results = rule_func(file_path, tree)

                elif "java_class_naming_rule" == rule_name:

                    rule_results = rule_func(file_path, java_classes)

                elif "java_method_naming_rule" == rule_name:

                    rule_results = rule_func(file_path, java_methods)

                elif "java_dto_request_response_separation_rule" == rule_name:

                    rule_results = rule_func(file_path, java_classes)

                elif "python_layered_package_structure_rule" == rule_name:

                    rule_results = rule_func(file_path)

                elif "layered" in rule_name:

                    # java_layered_* 룰은 import 기반, python_layered_* 도 import 기반
                    rule_results = rule_func(file_path, imports)

                elif "fastapi_request_response_schema_rule" == rule_name:

                    rule_results = rule_func(file_path, python_classes)

                elif "fastapi" in rule_name:

                    rule_results = rule_func(file_path, imports)

                elif "spring" in rule_name:

                    rule_results = rule_func(file_path, content)

                else:

                    rule_results = rule_func(file_path)

                if rule_results:

                    for r in rule_results:

                        if isinstance(r, RuleResult):
                            results.append(r)

            except Exception as e:

                print(f"Rule error {rule_name} in {file_path}: {e}")

    return results
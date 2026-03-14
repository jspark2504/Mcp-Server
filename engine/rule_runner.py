# rule 실행 및 결과 수집
import importlib
from engine.file_scanner import read_file
from engine.ast_parser import parse_python_ast, extract_python_imports
from models.result_model import RuleResult


RULE_MODULES = [
    "rules.language.python.pep8_rules",
    "rules.language.java.naming_rules",
    "rules.architecture.layered.python_layered_rules",
    "rules.architecture.layered.java_layered_rules",
    "rules.framework.fastapi_rules",
    "rules.framework.spring_rules",
]


def load_rule_function(rule_name):

    for module_path in RULE_MODULES:

        module = importlib.import_module(module_path)

        if hasattr(module, rule_name):

            return getattr(module, rule_name)

    raise Exception(f"Rule not found: {rule_name}")


def run_rules(files, rule_names):

    results = []

    for file_path in files:

        content = read_file(file_path)

        if not content:
            continue

        lines = content.split("\n")

        tree = None
        imports = []

        # python AST 파싱
        if file_path.endswith(".py"):

            tree = parse_python_ast(content)

            if tree:
                imports = extract_python_imports(tree)

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

                elif "layered" in rule_name:

                    rule_results = rule_func(file_path, imports)

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
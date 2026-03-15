import re
from models.result_model import create_result


def java_class_naming_rule(file_path, classes):
    """클래스명이 PascalCase가 아니면 위반 추가."""

    results = []

    for cls in classes:

        if not re.match(r'^[A-Z][A-Za-z0-9]+$', cls):

            results.append(
                create_result(
                    "java_class_naming_rule",
                    file_path,
                    f"Class '{cls}' should follow PascalCase"
                )
            )

    return results


def java_method_naming_rule(file_path, methods):
    """메서드명이 camelCase가 아니면 위반 추가."""

    results = []

    for method in methods:

        if not re.match(r'^[a-z][A-Za-z0-9]+$', method):

            results.append(
                create_result(
                    "java_method_naming_rule",
                    file_path,
                    f"Method '{method}' should follow camelCase"
                )
            )

    return results
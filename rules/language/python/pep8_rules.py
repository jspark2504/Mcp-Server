import re
from models.result_model import create_result


def pep8_variable_naming_rule(file_path, tree):

    results = []

    for node in tree.body:

        if hasattr(node, "targets"):

            for target in node.targets:

                if hasattr(target, "id"):

                    name = target.id

                    if not re.match(r'^[a-z_]+$', name):

                        results.append(
                            create_result(
                                "pep8_variable_naming_rule",
                                file_path,
                                f"Variable '{name}' should be snake_case"
                            )
                        )

    return results


def pep8_line_length_rule(file_path, lines):

    results = []

    for i, line in enumerate(lines):

        if len(line) > 120:

            results.append(
                create_result(
                    "pep8_line_length_rule",
                    file_path,
                    "Line exceeds 120 characters",
                    line=i + 1
                )
            )

    return results
from models.result_model import create_result


def spring_controller_annotation_rule(file_path, content):

    results = []

    if "controller" in file_path.lower():

        if "@RestController" not in content and "@Controller" not in content:

            results.append(
                create_result(
                    "spring_controller_annotation_rule",
                    file_path,
                    "Spring controller should use @RestController or @Controller"
                )
            )

    return results
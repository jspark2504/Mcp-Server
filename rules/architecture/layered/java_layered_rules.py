from models.result_model import create_result


def java_controller_repository_violation(file_path, imports):

    results = []

    if "controller" in file_path.lower():

        for imp in imports:

            if "repository" in imp.lower():

                results.append(
                    create_result(
                        "java_controller_repository_violation",
                        file_path,
                        "Controller should not directly use Repository"
                    )
                )

    return results
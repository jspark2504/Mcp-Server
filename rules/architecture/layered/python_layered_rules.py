from models.result_model import create_result


def python_layered_router_repository_violation(file_path, imports):

    results = []

    if "router" in file_path:

        for imp in imports:

            if "repository" in imp:

                results.append(
                    create_result(
                        "python_layered_router_repository_violation",
                        file_path,
                        "Router should not directly import repository"
                    )
                )

    return results
from models.result_model import create_result


def python_layered_router_repository_rule(file_path, imports):

    results = []

    if "router" in file_path:

        for imp in imports:

            if "repository" in imp:

                results.append(
                    create_result(
                        "python_layered_router_repository_rule",
                        file_path,
                        "Router should not directly import repository"
                    )
                )

    return results


def python_layered_router_service_rule(file_path, imports):

    results = []

    if "router" in file_path:

        has_service_import = any("service" in imp for imp in imports)

        if not has_service_import:
            results.append(
                create_result(
                    "python_layered_router_service_rule",
                    file_path,
                    "Router should depend on service layer (import service module)"
                )
            )

    return results


def python_layered_service_repository_rule(file_path, imports):

    results = []

    if "service" in file_path:

        for imp in imports:

            if "controller" in imp or "router" in imp:
                results.append(
                    create_result(
                        "python_layered_service_repository_rule",
                        file_path,
                        "Service should not depend on router/controller layer"
                    )
                )

    return results


def python_layered_package_structure_rule(file_path):
    """
    레이어드 패키지 구조: router/controller 파일이 repository 또는 service 패키지 하위에 있으면 안 됨.
    """
    results = []
    path_norm = file_path.lower().replace("\\", "/")

    if "repository" in path_norm and ("router" in path_norm or "controller" in path_norm):
        results.append(
            create_result(
                "python_layered_package_structure_rule",
                file_path,
                "Router/controller should not be placed under repository package",
            )
        )

    if "service" in path_norm and "router" in path_norm:
        results.append(
            create_result(
                "python_layered_package_structure_rule",
                file_path,
                "Router should not be placed under service package",
            )
        )

    return results
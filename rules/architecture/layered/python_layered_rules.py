from models.result_model import create_result


def python_layered_router_repository_rule(file_path, imports):
    """router 파일이 repository를 import하면 레이어 위반으로 추가."""

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
    """router 파일인데 service를 import하지 않으면 위반 추가."""

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
    """service 파일이 controller/router를 import하면 역의존 위반으로 추가."""

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
    """경로에 repository+router/controller 또는 service+router가 같이 있으면 패키지 구조 위반 추가."""

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
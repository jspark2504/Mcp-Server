from models.result_model import create_result


def java_layered_controller_repository_rule(file_path, imports):

    results = []

    if "controller" in file_path.lower():

        for imp in imports:

            if "repository" in imp.lower():

                results.append(
                    create_result(
                        "java_layered_controller_repository_rule",
                        file_path,
                        "Controller should not directly use Repository"
                    )
                )

    return results


def java_layered_controller_service_rule(file_path, imports):

    results = []

    if "controller" in file_path.lower():

        has_service_import = any("service" in imp.lower() for imp in imports)

        if not has_service_import:
            results.append(
                create_result(
                    "java_layered_controller_service_rule",
                    file_path,
                    "Controller should depend on service layer (import service)"
                )
            )

    return results


def java_layered_service_repository_rule(file_path, imports):

    results = []

    if "service" in file_path.lower():

        for imp in imports:

            if "controller" in imp.lower():
                results.append(
                    create_result(
                        "java_layered_service_repository_rule",
                        file_path,
                        "Service should not depend on controller layer"
                    )
                )

    return results


def java_service_transaction_rule(file_path, content):

    results = []

    if "service" in file_path.lower():

        has_transactional = "@Transactional" in content

        if not has_transactional:
            results.append(
                create_result(
                    "java_service_transaction_rule",
                    file_path,
                    "Service layer should define transaction boundary (@Transactional) for data-changing methods"
                )
            )

    return results


def java_service_constructor_injection_rule(file_path, content):

    results = []

    if "service" in file_path.lower():

        uses_field_injection = "@Autowired" in content and "class" in content and "@" in content

        if uses_field_injection:
            results.append(
                create_result(
                    "java_service_constructor_injection_rule",
                    file_path,
                    "Service should prefer constructor injection over field injection (@Autowired on fields)"
                )
            )

    return results


def java_service_return_dto_rule(file_path, content):

    results = []

    if "service" in file_path.lower():

        # 매우 단순한 휴리스틱: 'ResponseEntity<' 나 'Dto' 를 반환 타입에서 찾아봄
        returns_entity_directly = "ResponseEntity<" in content or "Entity>" in content

        if returns_entity_directly:
            results.append(
                create_result(
                    "java_service_return_dto_rule",
                    file_path,
                    "Service should return DTO instead of exposing persistence entities directly"
                )
            )

    return results
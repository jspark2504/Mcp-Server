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


def spring_service_annotation_rule(file_path, content):

    results = []

    if "service" in file_path.lower():

        if "@Service" not in content:

            results.append(
                create_result(
                    "spring_service_annotation_rule",
                    file_path,
                    "Spring service should use @Service"
                )
            )

    return results


def spring_repository_annotation_rule(file_path, content):

    results = []

    if "repository" in file_path.lower():

        if "@Repository" not in content:

            results.append(
                create_result(
                    "spring_repository_annotation_rule",
                    file_path,
                    "Spring repository should use @Repository"
                )
            )

    return results


def spring_controller_response_wrapper_rule(file_path, content):

    results = []

    if "controller" in file_path.lower():

        uses_response_entity = "ResponseEntity<" in content
        uses_common_wrapper = "ApiResponse<" in content or "CommonResponse<" in content

        if not (uses_response_entity or uses_common_wrapper):
            results.append(
                create_result(
                    "spring_controller_response_wrapper_rule",
                    file_path,
                    "Controller should use a response wrapper (ResponseEntity or common ApiResponse) for HTTP responses",
                )
            )

    return results
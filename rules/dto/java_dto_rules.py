from models.result_model import create_result


def java_dto_request_response_separation_rule(file_path, classes):

    results = []

    if "dto" not in file_path.lower():
        return results

    has_request = any(cls.endswith("Request") for cls in classes)
    has_response = any(cls.endswith("Response") for cls in classes)

    if not (has_request or has_response):
        results.append(
            create_result(
                "java_dto_request_response_separation_rule",
                file_path,
                "DTO classes should be clearly separated into *Request and *Response types",
            )
        )

    return results


from models.result_model import create_result


def fastapi_router_rule(file_path, imports):

    results = []

    if "router" in file_path:

        found = False

        for imp in imports:

            if "fastapi" in imp.lower():
                found = True

        if not found:

            results.append(
                create_result(
                    "fastapi_router_rule",
                    file_path,
                    "Router should import FastAPI router"
                )
            )

    return results


def fastapi_dependency_rule(file_path, imports):

    results = []

    if "router" in file_path:

        has_fastapi_import = any("fastapi" in imp.lower() for imp in imports)

        # 아주 단순한 규칙: FastAPI 라우터 파일인데 fastapi를 import하지 않으면 경고
        if not has_fastapi_import:
            results.append(
                create_result(
                    "fastapi_dependency_rule",
                    file_path,
                    "FastAPI router should explicitly import fastapi (for Depends, APIRouter, etc.)"
                )
            )

    return results


def fastapi_request_response_schema_rule(file_path, classes):
    """
    스키마/모델 파일에서 Request/Response 구분이 되어 있는지 검사.
    클래스명이 *Request, *Response, *Schema 등으로 끝나면 구분된 것으로 봄.
    """
    results = []

    path_lower = file_path.lower().replace("\\", "/")
    if "schema" not in path_lower and "model" not in path_lower and "dto" not in path_lower and "schemas" not in path_lower and "models" not in path_lower:
        return results

    has_request = any(
        c.endswith("Request") or "Request" in c
        for c in classes
    )
    has_response = any(
        c.endswith("Response") or "Response" in c
        for c in classes
    )
    has_schema = any(
        c.endswith("Schema") or "Schema" in c
        for c in classes
    )

    if not (has_request or has_response or has_schema) and classes:
        results.append(
            create_result(
                "fastapi_request_response_schema_rule",
                file_path,
                "API schema/model should separate request and response (e.g. *Request, *Response, *Schema)",
            )
        )

    return results
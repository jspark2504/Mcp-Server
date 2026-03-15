from models.result_model import create_result


def fastapi_router_rule(file_path, imports):
    """router 파일인데 fastapi를 import하지 않으면 위반 추가."""

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
    """router 파일인데 fastapi 모듈을 import하지 않으면 Depends/APIRouter 등 사용 누락으로 위반 추가."""

    results = []

    if "router" in file_path:

        has_fastapi_import = any("fastapi" in imp.lower() for imp in imports)

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
    """schema/model/dto 경로의 파일에서 클래스명이 *Request/*Response/*Schema가 하나도 없으면 위반 추가."""

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
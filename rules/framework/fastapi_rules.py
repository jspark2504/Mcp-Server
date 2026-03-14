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
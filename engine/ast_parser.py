# 코드 AST 파싱
import ast


def parse_python_ast(file_content):
    try:
        tree = ast.parse(file_content)
        return tree
    except Exception:
        return None


def extract_python_imports(tree):

    imports = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append(name.name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return imports


def extract_python_classes(tree):

    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)

    return classes


def extract_python_functions(tree):

    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)

    return functions
# 코드 AST 파싱
import ast


def parse_python_ast(file_content):
    """Python 소스 문자열을 ast.parse로 파싱해 AST 반환. 실패 시 None."""

    try:
        tree = ast.parse(file_content)
        return tree
    except Exception:
        return None


def extract_python_imports(tree):
    """AST에서 Import/ImportFrom 노드를 순회해 모듈·이름 리스트 반환."""

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
    """AST에서 ClassDef 노드를 순회해 클래스 이름 리스트 반환."""

    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)

    return classes


def extract_python_functions(tree):
    """AST에서 FunctionDef 노드를 순회해 함수 이름 리스트 반환."""

    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)

    return functions
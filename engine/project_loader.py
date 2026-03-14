# 프로젝트 경로 / git 로드
import os


class Project:

    def __init__(self, root_path):

        self.root_path = root_path
        self.has_git = False
        self.project_name = os.path.basename(root_path)

        self._detect_git()

    def _detect_git(self):

        git_path = os.path.join(self.root_path, ".git")

        if os.path.exists(git_path):
            self.has_git = True


def load_project(project_path: str):

    if not os.path.exists(project_path):
        raise Exception(f"Project path not found: {project_path}")

    if not os.path.isdir(project_path):
        raise Exception("Project path must be directory")

    project = Project(project_path)

    return project
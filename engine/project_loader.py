# 프로젝트 경로 / git 로드
import os


class Project:
    """분석 대상 프로젝트의 루트 경로, Git 여부, 프로젝트 이름을 담는 모델."""

    def __init__(self, root_path):
        """root_path 기준으로 경로·Git·이름을 설정하고 _detect_git 호출."""

        self.root_path = root_path
        self.has_git = False
        self.project_name = os.path.basename(root_path)

        self._detect_git()

    def _detect_git(self):
        """루트 하위 .git 존재 여부로 has_git 플래그 설정."""

        git_path = os.path.join(self.root_path, ".git")

        if os.path.exists(git_path):
            self.has_git = True


def load_project(project_path: str):
    """경로 존재·디렉터리 여부 검사 후 Project 인스턴스 생성해 반환. 실패 시 예외."""

    if not os.path.exists(project_path):
        raise Exception(f"Project path not found: {project_path}")

    if not os.path.isdir(project_path):
        raise Exception("Project path must be directory")

    project = Project(project_path)

    return project
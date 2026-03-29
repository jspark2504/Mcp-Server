# Project Check Spec

이 문서는 프로젝트 자동 점검을 위한 기준 문서입니다.
README와 분리해, "지켜야 할 규칙"만 간단히 적습니다.

## Language
- python or java 중 하나를 명시한다.

## Architecture
- Layered architecture를 따른다: controller/router -> service -> repository.
- 상위 레이어가 하위 레이어를 우회 호출하지 않는다.

## Framework
- Python(FastAPI): router, dependency, request/response schema 규칙을 따른다.
- Java(Spring): controller/service/repository annotation 규칙을 따른다.

## Style & Testing
- Python은 PEP8 네이밍/라인 길이 규칙을 지킨다.
- Java는 class/method naming 규칙을 지킨다.
- 테스트 도구(pytest/junit)를 사용하면 문서에도 명시한다.

## Security
- `.env`와 API key/token은 저장소에 평문 커밋하지 않는다.
- 금지 라이브러리(예: lombok)는 사용 금지 또는 명시적 예외 사유를 기록한다.

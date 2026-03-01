"""
메인 진입점.
이미지 예시처럼 MCP 서버를 HTTP(0.0.0.0:8000)로 실행합니다.
"""
from server import mcp


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)

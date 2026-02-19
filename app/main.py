import os
from dotenv import load_dotenv

from board.adapter.input.web.board_router import board_router
from config.database.session import Base, engine

load_dotenv()


from fastapi import FastAPI

app = FastAPI()


app.include_router(board_router, prefix="/board")
# 앱 실행
if __name__ == "__main__":
    import uvicorn
    host = os.getenv("APP_HOST")
    port = int(os.getenv("APP_PORT"))
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    uvicorn.run(app, host=host, port=port)

from fastapi import APIRouter, Depends, Query, Body
from fastapi.responses import JSONResponse

# from utility.session_helper import get_current_user
# from account.application.usecase.account_usecase import AccountUseCase
# from account.infrastructure.repository.account_repository_impl import AccountRepositoryImpl
from board.adapter.input.web.request.create_board_request import CreateBoardRequest
# from board.adapter.input.web.request.update_board_request import UpdateBoardRequest
# from board.adapter.input.web.response.board_list_response import BoardListResponse
# from board.application.usecase.board_usecase import BoardUsecase
# from board.infrastructure.repository.board_repository_impl import BoardRepositoryImpl
from datetime import datetime

board_router = APIRouter(tags=["board"])
# board_repository_impl = BoardRepositoryImpl()
# board_usecase = BoardUsecase(board_repository_impl)
#
# account_repository_impl = AccountRepositoryImpl()
# account_usecase = AccountUseCase(account_repository_impl)

# 세션으로 사용자 확인
from fastapi import HTTPException

# 게시글 생성
@board_router.post("/create")
async def create_board(
    request_data: CreateBoardRequest,
):
    print("=== 게시글 생성 요청 ===")
    print(f"title: {request_data.title}")
    print(f"content: {request_data.content}")
    print("=======================")

    return JSONResponse({
        "message": "print 테스트 완료",
        "title": request_data.title,
        "created_at": datetime.now().isoformat()
    })
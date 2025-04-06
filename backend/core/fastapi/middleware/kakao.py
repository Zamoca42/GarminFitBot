from fastapi import Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from api.common.schema import (
    KakaoResponse,
    MessageButton,
    Template,
    TextCard,
    WebLinkButton,
)
from app.model import User
from app.service.token_service import TempTokenService
from core.config import FRONTEND_URL, KAKAO_BOT_ID
from core.db import get_session


class KakaoBotMiddleware(BaseHTTPMiddleware):
    """카카오톡 봇 ID 검증 미들웨어"""

    async def dispatch(self, request: Request, call_next) -> JSONResponse:
        try:
            if "/parse-date" in request.url.path:
                response = await call_next(request)
                return response
            
            if "/kakao" in request.url.path:
                body = await request.json()

                if "bot" not in body or body["bot"]["id"] != KAKAO_BOT_ID:
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": "유효하지 않은 카카오톡 봇입니다."},
                    )

            response = await call_next(request)
            return response
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": str(e)},
            )


class KakaoUserMiddleware(BaseHTTPMiddleware):
    """카카오톡 유저 서비스 연결 검증 미들웨어"""

    def __init__(self, app, session_factory=get_session):
        super().__init__(app)
        self.session_factory = session_factory
        self.kakao_bot_signup_path = "/auth/kakao/signup"

    async def _get_user(self, session: AsyncSession, user_key: str) -> User:
        """사용자 조회"""
        result = await session.execute(
            select(User).where(User.kakao_client_id == user_key)
        )
        return result.scalar_one_or_none()

    async def _handle_existing_user(self, user: User) -> JSONResponse:
        """이미 등록된 사용자 처리"""
        kakao_response = KakaoResponse(
            template=Template(
                outputs=[
                    {
                        "textCard": TextCard(
                            title="서비스 연결 완료",
                            description=f"{user.full_name}님,\n 가민 계정은 이미 연결되어 있어요! 🙌\n"
                            f"이제 데이터 수집이나 건강 분석 같은\n 기능들을 바로 이용하실 수 있어요.\n\n",
                            buttons=[
                                MessageButton(
                                    label="연결된 프로필 조회",
                                    messageText="프로필 조회",
                                )
                            ],
                        )
                    }
                ]
            )
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=kakao_response.model_dump(),
        )

    async def _handle_unregistered_user(
        self, session: AsyncSession, user_key: str
    ) -> JSONResponse:
        """미등록 사용자 처리"""
        temp_token_service = TempTokenService(session)
        await temp_token_service.create_signup_token(user_key)

        kakao_response = KakaoResponse(
            template=Template(
                outputs=[
                    {
                        "textCard": TextCard(
                            title="서비스 연결 필요",
                            description="가민 커넥트와 챗봇 서비스가 연결되어 있지 않습니다.\n아래 버튼을 클릭하여 서비스를 연결해주세요.",
                            buttons=[
                                WebLinkButton(
                                    action="webLink",
                                    label="서비스 연결",
                                    webLinkUrl=f"{FRONTEND_URL}/signup/{user_key}",
                                )
                            ],
                        )
                    }
                ]
            )
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=kakao_response.model_dump(),
        )

    async def dispatch(self, request: Request, call_next) -> JSONResponse:
        try:
            if "/kakao" in request.url.path:
                body = await request.json()

                user_key = body.get("userRequest", {}).get("user", {}).get("id") or body.get("user", {}).get("id")
                if not user_key:
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"detail": "유저 ID가 없습니다."},
                    )

                async for session in self.session_factory():
                    user = await self._get_user(session, user_key)

                    # 회원가입 요청인데 이미 유저가 있는 경우
                    if self.kakao_bot_signup_path in request.url.path and user:
                        return await self._handle_existing_user(user)

                    # 회원가입이 아닌 요청인데 유저가 없는 경우
                    if self.kakao_bot_signup_path not in request.url.path and not user:
                        return await self._handle_unregistered_user(session, user_key)

            response = await call_next(request)
            return response
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": str(e)},
            )

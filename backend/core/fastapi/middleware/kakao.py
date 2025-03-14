from fastapi import Request, status
from sqlalchemy import select
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from api.common.schema import Button, KakaoResponse, Template, TextCard
from app.model import User
from core.config import FRONTEND_URL, KAKAO_BOT_ID
from core.db import get_session


class KakaoBotMiddleware(BaseHTTPMiddleware):
    """카카오톡 봇 ID 검증 미들웨어"""

    async def dispatch(self, request: Request, call_next) -> JSONResponse:
        try:
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

    async def dispatch(self, request: Request, call_next) -> JSONResponse:
        try:
            if (
                "/kakao" in request.url.path
                and "/auth/kakao/signup" not in request.url.path
            ):
                body = await request.json()

                # 유저 ID 추출
                user_key = body.get("userRequest", {}).get("user", {}).get("id")
                if not user_key:
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"detail": "유저 ID가 없습니다."},
                    )

                # DB에서 유저 조회
                async for session in get_session():
                    result = await session.execute(
                        select(User).where(User.kakao_client_id == user_key)
                    )
                    user = result.scalar_one_or_none()

                    if not user:
                        kakao_response = KakaoResponse(
                            template=Template(
                                outputs=[
                                    {
                                        "textCard": TextCard(
                                            title="서비스 연결 필요",
                                            description="가민 커넥트와 챗봇 서비스가 연결되어 있지 않습니다.\n아래 버튼을 클릭하여 서비스를 연결해주세요.",
                                            buttons=[
                                                Button(
                                                    action="webLink",
                                                    label="서비스 연결",
                                                    webLinkUrl=f"{FRONTEND_URL}/auth/kakao/signup/{user_key}",
                                                )
                                            ],
                                        )
                                    }
                                ]
                            )
                        )
                        return JSONResponse(
                            status_code=status.HTTP_403_FORBIDDEN,
                            content=kakao_response.model_dump(),
                        )

            response = await call_next(request)
            return response
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": str(e)},
            )

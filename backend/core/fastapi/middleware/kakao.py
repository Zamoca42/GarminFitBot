from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from core.config import KAKAO_BOT_ID


class KakaoBotMiddleware(BaseHTTPMiddleware):
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

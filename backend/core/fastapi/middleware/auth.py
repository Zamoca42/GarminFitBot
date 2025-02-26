from typing import Optional, Tuple

from fastapi.security import HTTPBearer
from garth import Client as GarthClient
from starlette.authentication import AuthenticationBackend
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection

from app.service.token_service import TokenService

security = HTTPBearer()
token_service = TokenService()


class GarminAuthUser:
    def __init__(self, user_info: dict, garmin_client: GarthClient):
        self.user_info = user_info
        self.garmin_client = garmin_client
        self.is_authenticated = True


class GarminAuthBackend(AuthenticationBackend):
    async def authenticate(
        self, conn: HTTPConnection
    ) -> Tuple[bool, Optional[GarminAuthUser]]:
        if not self._should_verify(conn.url.path):
            return False, None

        try:
            auth_header = conn.headers.get("Authorization")
            if not auth_header:
                return False, None

            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return False, None

            user_info = token_service.decode_token(token)
            garmin_client = token_service.create_garmin_client(user_info["oauth1Token"])

            return True, GarminAuthUser(user_info, garmin_client)

        except Exception:
            return False, None

    def _should_verify(self, path: str) -> bool:
        public_paths = {"/docs", "/redoc", "/openapi.json", "/health", "/auth/login"}
        return not any(path.startswith(p) for p in public_paths)


# 미들웨어 설정
auth_middleware = AuthenticationMiddleware(None, backend=GarminAuthBackend())

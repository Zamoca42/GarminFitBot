from fastapi import HTTPException, Request, status

from api.common.schema import ResponseModel
from api.v1.auth.schema import LoginRequest
from app.service import GarminAuthManager, TokenService


class AuthController:
    def __init__(self):
        self.auth_service = GarminAuthManager()
        self.token_service = TokenService()

    async def login(self, request: LoginRequest) -> ResponseModel:
        try:
            client = await self.auth_service.login(request.email, request.password)

            if isinstance(client, dict):
                return ResponseModel(message="MFA 필요", data=client)

            await self.auth_service.save_login_user(client)
            access_token = self.token_service.create_token(client)

            return ResponseModel(
                message="로그인 성공", data={"accessToken": access_token}
            )

        except Exception as e:
            print(f"Login error: {e}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    async def refresh_token(self, request: Request) -> ResponseModel:
        try:
            access_token = self.token_service.create_token(request.user.garmin_client)

            return ResponseModel(
                message="토큰 갱신 성공",
                data={"accessToken": access_token, "tokenType": "bearer"},
            )

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

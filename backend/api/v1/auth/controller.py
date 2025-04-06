from fastapi import HTTPException, Request, status

from api.common.schema import (
    KakaoRequest,
    KakaoResponse,
    ResponseModel,
    Template,
    TextCard,
    WebLinkButton,
)
from api.v1.auth.schema import LoginRequest, SignupRequest
from app.service import GarminAuthManager, TempTokenService, TokenService
from core.config import FRONTEND_URL


class AuthController:
    def __init__(
        self,
        auth_service: GarminAuthManager,
        token_service: TokenService,
        temp_token_service: TempTokenService,
    ):
        self.auth_service = auth_service
        self.token_service = token_service
        self.temp_token_service = temp_token_service

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

    async def handle_kakao_signup(self, request: KakaoRequest) -> KakaoResponse:
        try:
            user_key = request.userRequest.user.id
            await self.temp_token_service.create_signup_token(user_key)
            signup_url = f"{FRONTEND_URL}/signup/{user_key}"

            return KakaoResponse(
                template=Template(
                    outputs=[
                        {
                            "textCard": TextCard(
                                title="챗봇 서비스 연결을 시작을 시작합니다",
                                description="서비스 연결을 위해 아래 버튼을 클릭해주세요. \n\n웹 페이지가 열리고 가민 커넥트 계정을 입력하면 서비스 연결이 완료됩니다.",
                                buttons=[
                                    WebLinkButton(
                                        label="서비스 연결",
                                        webLinkUrl=signup_url,
                                    )
                                ],
                            )
                        }
                    ]
                )
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    async def verify_client(self, client_id: str) -> ResponseModel:
        try:
            is_valid = await self.temp_token_service.verify_signup_token(client_id)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="유효하지 않은 접근입니다.",
                )
            return ResponseModel(message="검증 성공", data={"is_valid": True})
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def signup(self, request: SignupRequest) -> ResponseModel:
        try:
            is_valid = await self.temp_token_service.verify_signup_token(
                request.client_id
            )
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="유효하지 않은 접근입니다.",
                )
            await self.temp_token_service.delete_signup_token(request.client_id)

            client = await self.auth_service.login(request.garmin_id, request.password)

            if isinstance(client, dict):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="MFA가 필요한 계정은 등록할 수 없습니다.",
                )

            await self.auth_service.save_login_user(
                client, kakao_client_id=request.client_id
            )

            return ResponseModel(message="회원가입 성공")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

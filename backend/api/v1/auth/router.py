from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPBearer

from api.common.schema import ResponseModel
from api.v1.auth.controller import AuthController
from api.v1.auth.schema import KakaoRequest, LoginRequest, SignupRequest
from app.service import GarminAuthManager, TempTokenService, TokenService
from core.db import AsyncSession, get_session

router = APIRouter(prefix="/auth", tags=["인증"])
security = HTTPBearer()


def get_auth_manager(session: AsyncSession = Depends(get_session)) -> GarminAuthManager:
    return GarminAuthManager(session)


def get_token_service() -> TokenService:
    return TokenService()


def get_temp_token_service(
    session: AsyncSession = Depends(get_session),
) -> TempTokenService:
    return TempTokenService(session)


def get_auth_controller(
    auth_manager: GarminAuthManager = Depends(get_auth_manager),
    token_service: TokenService = Depends(get_token_service),
    temp_token_service: TempTokenService = Depends(get_temp_token_service),
) -> AuthController:
    return AuthController(auth_manager, token_service, temp_token_service)


@router.post("/login", response_model=ResponseModel, summary="가민 계정 로그인")
async def login(
    request: LoginRequest, controller: AuthController = Depends(get_auth_controller)
):
    """가민 계정으로 로그인"""
    return await controller.login(request)


@router.post(
    "/refresh",
    response_model=ResponseModel,
    summary="토큰 갱신",
    dependencies=[Depends(security)],
)
async def refresh_token(
    request: Request, controller: AuthController = Depends(get_auth_controller)
):
    """토큰 갱신"""
    return await controller.refresh_token(request)


@router.post("/kakao/signup", summary="카카오톡 챗봇 회원가입 요청")
async def kakao_signup(
    request: KakaoRequest, controller: AuthController = Depends(get_auth_controller)
):
    """카카오톡 챗봇을 통한 회원가입 요청 처리"""
    return await controller.handle_kakao_signup(request)


@router.get(
    "/verify-client/{client_id}",
    response_model=ResponseModel,
    summary="회원가입 토큰 검증",
)
async def verify_client(
    client_id: str, controller: AuthController = Depends(get_auth_controller)
):
    """회원가입 토큰 검증"""
    return await controller.verify_client(client_id)


@router.post("/signup", response_model=ResponseModel, summary="회원가입")
async def signup(
    request: SignupRequest, controller: AuthController = Depends(get_auth_controller)
):
    """가민 계정으로 회원가입"""
    return await controller.signup(request)

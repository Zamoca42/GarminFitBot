from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPBearer

from api.common.schema import ResponseModel
from api.v1.auth.controller import AuthController
from api.v1.auth.schema import LoginRequest
from app.service import GarminAuthManager
from core.db import AsyncSession, get_session

router = APIRouter(prefix="/auth", tags=["인증"])
security = HTTPBearer()


def get_auth_manager(session: AsyncSession = Depends(get_session)) -> GarminAuthManager:
    return GarminAuthManager(session)


def get_auth_controller(
    auth_manager: GarminAuthManager = Depends(get_auth_manager),
) -> AuthController:
    return AuthController(auth_manager)


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

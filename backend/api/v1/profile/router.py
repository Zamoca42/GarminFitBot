from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPBearer

from api.common.schema import ResponseModel

from .controller import ProfileController

router = APIRouter(prefix="/profile", tags=["프로필"])
security = HTTPBearer()


def get_profile_controller():
    return ProfileController()


@router.get(
    "",
    response_model=ResponseModel,
    summary="사용자 프로필 조회",
    dependencies=[Depends(security)],
)
async def get_profile(
    request: Request, controller: ProfileController = Depends(get_profile_controller)
):
    """사용자 프로필 조회"""
    return await controller.get_profile(request)

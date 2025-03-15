from fastapi import APIRouter, Depends

from api.common.schema import KakaoRequest, KakaoResponse
from api.v1.kakao.controller import KakaoController

router = APIRouter(prefix="/kakao", tags=["카카오 챗봇"])


def get_kakao_controller() -> KakaoController:
    return KakaoController()


@router.post("/fit/collection", response_model=KakaoResponse)
async def request_data_collection(
    request: KakaoRequest,
    controller: KakaoController = Depends(get_kakao_controller),
):
    """
    카카오 챗봇에서 데이터 수집 작업 요청
    """
    return await controller.request_data_collection(request)

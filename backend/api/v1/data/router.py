from fastapi import APIRouter, Depends

from api.common.schema import KakaoRequest, KakaoResponse, ResponseModel
from api.v1.data.controller import DataController
from task import celery_app

router = APIRouter(prefix="/data", tags=["data"])


def get_data_controller() -> DataController:
    return DataController()


@router.post("/kakao/collect", response_model=KakaoResponse)
async def request_data_collection(
    request: KakaoRequest,
    controller: DataController = Depends(get_data_controller),
):
    """
    카카오 챗봇에서 데이터 수집 작업 요청
    """
    return await controller.request_data_collection(request)


@router.get("/status/{task_id}", response_model=ResponseModel)
async def get_task_status(
    task_id: str,
    controller: DataController = Depends(get_data_controller),
):
    """
    클라이언트 페이지에서 작업 상태 조회
    """
    return await controller.get_task_status(task_id)


@router.post("/revoke/{task_id}", response_model=ResponseModel)
async def revoke_task(
    task_id: str,
    controller: DataController = Depends(get_data_controller),
):
    """
    작업 취소
    """
    return await controller.revoke_task(task_id)

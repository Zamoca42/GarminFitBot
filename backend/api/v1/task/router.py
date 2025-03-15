from fastapi import APIRouter, Depends

from api.common.schema import ResponseModel
from api.v1.task.controller import TaskController

router = APIRouter(prefix="/task", tags=["작업"])


def get_task_controller() -> TaskController:
    return TaskController()


@router.get("/{task_id}/status", response_model=ResponseModel)
async def get_task_status(
    task_id: str,
    controller: TaskController = Depends(get_task_controller),
):
    """
    클라이언트 페이지에서 작업 상태 조회
    """
    return await controller.get_task_status(task_id)


@router.post("/{task_id}/revoke", response_model=ResponseModel)
async def revoke_task(
    task_id: str,
    controller: TaskController = Depends(get_task_controller),
):
    """
    작업 취소
    """
    return await controller.revoke_task(task_id)

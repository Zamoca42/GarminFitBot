import redis
from celery.result import AsyncResult
from fastapi import HTTPException
from fastapi import status as fastapi_status

from api.common.schema import ResponseModel
from api.v1.task.schema import TaskStatusResponse
from core.util.task_id import generate_celery_task_id


class TaskController:
    async def get_task_status(self, task_id: str) -> ResponseModel:
        """
        클라이언트 페이지에서 작업 상태 조회
        """
        try:
            celery_task_id = generate_celery_task_id(task_id)
            task = AsyncResult(celery_task_id)
            backend_state = task.backend.get_state(celery_task_id)

            if not task or not backend_state:
                raise HTTPException(
                    status_code=fastapi_status.HTTP_404_NOT_FOUND,
                    detail="작업을 찾을 수 없습니다.",
                )

            if backend_state == "PENDING":
                return ResponseModel(
                    message="작업 대기 중입니다.",
                    data=TaskStatusResponse(
                        task_id=task_id,
                        status="PENDING",
                        result=None,
                        error=None,
                    ),
                )

            task_status = task.state
            result = None
            error = None

            if task_status == "SUCCESS":
                result = task.result
            elif task_status == "FAILURE":
                error = str(task.result) if task.result else str(task.info)

            return ResponseModel(
                message="작업 상태 조회 완료",
                data=TaskStatusResponse(
                    task_id=task_id,
                    status=task_status,
                    result=result,
                    error=error,
                ),
            )
        except Exception as e:
            raise HTTPException(
                status_code=fastapi_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    async def revoke_task(self, task_id: str) -> ResponseModel:
        """
        작업 취소 및 삭제
        """
        try:
            celery_task_id = generate_celery_task_id(task_id)
            task = AsyncResult(celery_task_id)
            if task.state in ["PENDING", "STARTED", "PROGRESS"]:
                task.revoke(terminate=True)
            elif task.state in ["SUCCESS", "FAILURE"]:
                task.forget()
            else:
                raise HTTPException(
                    status_code=fastapi_status.HTTP_400_BAD_REQUEST,
                    detail="작업 취소 불가능",
                )

            return ResponseModel(message="작업 취소 및 삭제 완료")
        except Exception as e:
            raise HTTPException(
                status_code=fastapi_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

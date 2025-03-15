from celery.result import AsyncResult
from fastapi import HTTPException, status

from api.common.schema import ResponseModel
from api.v1.task.schema import TaskStatusResponse


class TaskController:
    async def get_task_status(self, task_id: str) -> ResponseModel:
        """
        클라이언트 페이지에서 작업 상태 조회
        """
        try:
            task = AsyncResult(task_id)

            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="작업을 찾을 수 없습니다.",
                )

            status = task.state
            result = None
            error = None

            if status == "SUCCESS":
                result = task.result
            elif status == "FAILURE":
                error = str(task.result) if task.result else str(task.info)

            return ResponseModel(
                message="작업 상태 조회 완료",
                data=TaskStatusResponse(
                    task_id=task_id,
                    status=status,
                    result=result,
                    error=error,
                ),
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    async def revoke_task(self, task_id: str) -> ResponseModel:
        """
        작업 취소 및 삭제
        """
        try:
            task = AsyncResult(task_id)
            if task.state in ["PENDING", "STARTED", "PROGRESS"]:
                task.revoke(terminate=True)
            elif task.state in ["SUCCESS", "FAILURE"]:
                task.forget()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="작업 취소 불가능"
                )

            return ResponseModel(message="작업 취소 및 삭제 완료")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

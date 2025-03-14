from datetime import datetime

from celery.result import AsyncResult
from fastapi import HTTPException, status

from api.common.schema import (
    Button,
    KakaoRequest,
    KakaoResponse,
    ResponseModel,
    SimpleText,
    Template,
    TextCard,
)
from api.v1.data.schema import TaskStatusResponse
from core.config import FRONTEND_URL
from task import celery_app, collect_user_fit_data


class DataController:
    async def request_data_collection(self, request: KakaoRequest) -> KakaoResponse:
        """
        카카오톡 챗봇에서 데이터 수집 작업 요청
        """
        try:
            user_key = request.userRequest.user.id
            user_timezone = request.userRequest.timezone
            date = request.action.detailParams["date"]["origin"]
            task_name = "collect-fit-data"
            task_id = f"{user_key}_{date}_{task_name}"
            task_result = AsyncResult(task_id)
            task_status_url = f"{FRONTEND_URL}/status/{user_key}/{date}/{task_name}"

            if task_result.status == "SUCCESS":
                return KakaoResponse(
                    template=Template(
                        outputs=[
                            {
                                "textCard": SimpleText(
                                    text="이미 해당 날짜의 데이터 수집이 완료되었습니다."
                                )
                            }
                        ]
                    )
                )
            elif task_result.status in ["STARTED", "PROGRESS"]:
                return KakaoResponse(
                    template=Template(
                        outputs=[
                            {
                                "textCard": TextCard(
                                    title="데이터 수집 진행 중",
                                    description="이미 해당 날짜의 데이터 수집이 진행 중입니다.\n아래 버튼을 클릭하여 진행 상황을 확인하실 수 있습니다.",
                                    buttons=[
                                        Button(
                                            action="webLink",
                                            label="진행 상황 확인",
                                            webLinkUrl=task_status_url,
                                        )
                                    ],
                                )
                            }
                        ]
                    )
                )

            # 새로운 작업 시작
            collect_user_fit_data.apply_async(
                kwargs={
                    "kakao_user_id": user_key,
                    "target_date": date,
                    "user_timezone": user_timezone,
                },
                task_id=task_id,
            )

            return KakaoResponse(
                template=Template(
                    outputs=[
                        {
                            "textCard": TextCard(
                                title="데이터 수집 시작",
                                description="데이터 수집이 시작되었습니다.\n작업 상태를 확인하려면 아래 버튼을 클릭해주세요.",
                                buttons=[
                                    Button(
                                        action="webLink",
                                        label="작업 상태 확인",
                                        webLinkUrl=task_status_url,
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

    async def get_task_status(self, task_id: str) -> ResponseModel:
        """
        클라이언트 페이지에서 작업 상태 조회
        """
        try:
            # Celery 작업 상태 조회
            task = celery_app.AsyncResult(task_id)

            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="작업을 찾을 수 없습니다.",
                )

            # 작업 상태 매핑
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
            task = celery_app.AsyncResult(task_id)
            if task.state in ["PENDING", "STARTED", "PROGRESS"]:
                task.revoke(terminate=True)
            elif task.state in ["SUCCESS", "FAILURE"]:
                task.forget()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="작업 취소 불가능"
                )

            return ResponseModel(message="작업 취소 완료")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

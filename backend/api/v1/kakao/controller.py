from datetime import datetime

import pytz
from celery.result import AsyncResult
from fastapi import HTTPException, status

from api.common.schema import (
    Button,
    KakaoRequest,
    KakaoResponse,
    SimpleText,
    Template,
    TextCard,
)
from core.config import FRONTEND_URL
from core.util.redis import is_duplicate_request
from core.util.task_id import generate_celery_task_id, generate_task_id, task_id_to_path
from task import analysis_health_query, collect_fit_data


class KakaoController:
    async def request_data_collection(self, request: KakaoRequest) -> KakaoResponse:
        """
        카카오톡 챗봇에서 데이터 수집 작업 요청
        """
        try:
            user_key = request.userRequest.user.id
            user_timezone = request.userRequest.timezone
            date = request.action.detailParams["date"]["origin"]
            task_name = collect_fit_data.name
            task_id = generate_task_id(user_key, date, task_name)
            celery_task_id = generate_celery_task_id(task_id)
            task_result = AsyncResult(celery_task_id)
            task_status_url = f"{FRONTEND_URL}/{task_id_to_path(task_id)}/status"

            if task_result.status == "SUCCESS":
                return KakaoResponse(
                    template=Template(
                        outputs=[
                            {
                                "simpleText": SimpleText(
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

            collect_fit_data.apply_async(
                kwargs={
                    "kakao_client_id": user_key,
                    "target_date": date,
                    "user_timezone": user_timezone,
                },
                task_id=celery_task_id,
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

    async def request_health_analysis(self, request: KakaoRequest) -> KakaoResponse:
        """
        카카오톡 챗봇에서 건강 분석 작업 요청
        """
        try:
            user_key = request.userRequest.user.id
            user_timezone = request.userRequest.timezone
            user_query = request.userRequest.utterance
            timezone = pytz.timezone(user_timezone) if user_timezone else pytz.utc
            date = datetime.now(timezone).strftime("%Y-%m-%d")
            task_name = analysis_health_query.name
            task_id = generate_task_id(user_key, date, task_name, user_query)
            celery_task_id = generate_celery_task_id(task_id)
            task_result = AsyncResult(celery_task_id)
            task_status_url = f"{FRONTEND_URL}/{task_id_to_path(task_id)}/status"

            if await is_duplicate_request(task_id):
                return KakaoResponse(
                    template=Template(
                        outputs=[
                            {
                                "textCard": TextCard(
                                    title="분석 중복 요청",
                                    description="이미 분석이 진행 되어 중복 요청을 받지 않습니다.",
                                    buttons=[
                                        Button(
                                            action="webLink",
                                            label="결과 확인",
                                            webLinkUrl=task_status_url,
                                        )
                                    ],
                                )
                            }
                        ]
                    )
                )

            if task_result.status == "SUCCESS":
                return KakaoResponse(
                    template=Template(
                        outputs=[
                            {
                                "textCard": TextCard(
                                    title="분석 완료",
                                    description="분석이 완료되었습니다.\n아래 버튼을 클릭하여 결과를 확인하실 수 있습니다.",
                                    buttons=[
                                        Button(
                                            action="webLink",
                                            label="결과 확인",
                                            webLinkUrl=task_status_url,
                                        )
                                    ],
                                )
                            }
                        ]
                    )
                )
            elif task_result.status == "PROGRESS":
                return KakaoResponse(
                    template=Template(
                        outputs=[
                            {
                                "textCard": TextCard(
                                    title="분석 진행 중",
                                    description="분석이 진행 중입니다.\n아래 버튼을 클릭하여 진행 상황을 확인하실 수 있습니다.",
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

            analysis_health_query.apply_async(
                kwargs={
                    "kakao_client_id": user_key,
                    "query": user_query,
                    "user_timezone": user_timezone,
                },
                task_id=celery_task_id,
            )

            return KakaoResponse(
                template=Template(
                    outputs=[
                        {
                            "textCard": TextCard(
                                title="건강 분석 시작",
                                description="건강 분석이 시작되었습니다.\n작업 상태를 확인하려면 아래 버튼을 클릭해주세요.",
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

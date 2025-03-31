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
from core.util.aws import trigger_scale_out_event
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
                                    text="해당 날짜의 데이터는 이미 수집이 완료되었어요.\n다음 날 다시 요청해 주세요 😊"
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
                                    description="이미 데이터 수집이 진행 중이에요!\n아래 버튼을 눌러 현재 상황을 확인해 보세요 👇",
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

            trigger_scale_out_event()
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
                                description="데이터 수집을 시작했어요!\n작업 상태는 아래 버튼에서 확인하실 수 있어요 👍",
                                buttons=[
                                    Button(
                                        action="webLink",
                                        label="결과 확인하기",
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
                                    description="이미 해당 요청에 대한 분석이 진행 중이에요 😊\n결과는 아래 버튼을 눌러 확인하실 수 있어요.",
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
                                    description="분석이 모두 완료되었어요!\n아래 버튼을 눌러 결과를 확인해 보세요 🎉",
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
            elif task_result.status == "STARTED":
                return KakaoResponse(
                    template=Template(
                        outputs=[
                            {
                                "textCard": TextCard(
                                    title="AI가 건강 데이터 분석을 진행 중입니다",
                                    description="지금 AI가 열심히 분석 중이에요 🔍\n아래 버튼으로 진행 상황을 확인해 보세요.",
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

            trigger_scale_out_event()
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
                                title="AI가 건강 데이터 분석을 시작합니다",
                                description="AI가 건강 데이터를 분석하기 시작했어요! 💪\n분석이 끝나면 아래 버튼을 눌러 결과를 확인해 주세요.",
                                buttons=[
                                    Button(
                                        action="webLink",
                                        label="결과 확인하기",
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

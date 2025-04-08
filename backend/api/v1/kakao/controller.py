import logging
from datetime import datetime

import pytz
from celery.result import AsyncResult
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.common.schema import (
    KakaoRequest,
    KakaoResponse,
    SimpleText,
    Template,
    TextCard,
    WebLinkButton,
)
from api.common.schema.date_parser import DateParserRequest, DateParserResponse
from app.model import User
from app.service import DateParserService, TokenService
from core.config import FRONTEND_URL
from core.util.redis import is_duplicate_request
from core.util.task_id import generate_celery_task_id, generate_task_id, task_id_to_path
from task import analysis_health_query, collect_fit_data

logger = logging.getLogger(__name__)


class KakaoController:
    def __init__(
        self,
        session: AsyncSession,
        token_service: TokenService,
        date_parser_service: DateParserService,
    ):
        self.session = session
        self.token_service = token_service
        self.date_parser_service = date_parser_service

    async def request_data_collection(self, request: KakaoRequest) -> KakaoResponse:
        """
        카카오톡 챗봇에서 데이터 수집 작업 요청
        """
        logger.info(f"데이터 수집 요청: {request}")
        try:
            user_key = request.userRequest.user.id
            user_timezone = request.userRequest.timezone
            detail_params = request.action.detailParams
            formatted_date = detail_params["date"]["value"]
            origin_date = detail_params["date"]["origin"]
            task_name = collect_fit_data.name
            task_id = generate_task_id(user_key, formatted_date, task_name)
            celery_task_id = generate_celery_task_id(task_id)
            task_result = AsyncResult(celery_task_id)
            task_status_url = f"{FRONTEND_URL}/{task_id_to_path(task_id)}/status"

            if task_result.status == "SUCCESS":
                return KakaoResponse(
                    template=Template(
                        outputs=[
                            {
                                "simpleText": SimpleText(
                                    text=f"요청하신 수집일: {origin_date}\n"
                                    f"수집한 날짜: {formatted_date}\n"
                                    f"수집이 완료되었어요.\n"
                                    f"다음 날 다시 요청해 주세요 😊"
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
                                        WebLinkButton(
                                            label="진행 상황 확인",
                                            webLinkUrl=task_status_url,
                                        )
                                    ],
                                )
                            }
                        ]
                    )
                )

            # trigger_scale_out_event()
            collect_fit_data.apply_async(
                kwargs={
                    "kakao_client_id": user_key,
                    "target_date": formatted_date,
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
                                    WebLinkButton(
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
            logger.error(f"데이터 수집 요청 오류: {e}")
            return KakaoResponse(
                template=Template(
                    outputs=[
                        {
                            "simpleText": SimpleText(
                                text=f"데이터 수집 오류가 발생했어요.\n잠시 후 다시 시도해 주세요."
                            )
                        }
                    ]
                )
            )

    async def request_health_analysis(self, request: KakaoRequest) -> KakaoResponse:
        """
        카카오톡 챗봇에서 건강 데이터 분석 작업 요청
        """
        logger.info(f"건강 데이터 분석 요청: {request}")
        try:
            user_key = request.userRequest.user.id
            user_timezone = request.userRequest.timezone
            user_query = request.userRequest.utterance
            analysis_intent = (
                request.action.params["analysis_intent"]
                or request.action.params["analysis_intent1"]
            )
            user_analysis_intent = (
                "general"
                if analysis_intent is None or str(analysis_intent).strip() == ""
                else str(analysis_intent)
            )
            timezone = pytz.timezone(user_timezone) if user_timezone else pytz.utc
            date = datetime.now(timezone).strftime("%Y-%m-%d")
            task_name = analysis_health_query.name
            task_id = generate_task_id(
                user_key, date, task_name, user_analysis_intent, user_query
            )
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
                                        WebLinkButton(
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
                                        WebLinkButton(
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
                                        WebLinkButton(
                                            label="진행 상황 확인",
                                            webLinkUrl=task_status_url,
                                        )
                                    ],
                                )
                            }
                        ]
                    )
                )

            # trigger_scale_out_event()
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
                                    WebLinkButton(
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

    async def get_garmin_profile(self, request: KakaoRequest) -> KakaoResponse:
        """
        카카오톡 챗봇에서 연결된 가민 프로필 정보 조회
        """
        logger.info(f"가민 프로필 조회 요청: {request}")
        try:
            user_key = request.userRequest.user.id
            result = await self.session.execute(
                select(User).where(User.kakao_client_id == user_key)
            )
            user = result.scalar_one_or_none()

            oauth1_token = {
                "oauth_token": user.oauth_token,
                "oauth_token_secret": user.oauth_token_secret,
                "domain": user.domain,
            }
            garmin_client = self.token_service.create_garmin_client(oauth1_token)

            try:
                profile = garmin_client.user_profile

                full_name = profile.get("fullName", "")
                email = profile.get("userName", "")

                connect_last_sync_info = garmin_client.connectapi(
                    "/wellness-service/wellness/syncTimestamp"
                )
                user_timezone = request.userRequest.timezone or "Asia/Seoul"
                tz = pytz.timezone(user_timezone)

                if isinstance(connect_last_sync_info, str):
                    try:
                        sync_time = datetime.strptime(
                            connect_last_sync_info, "%Y-%m-%dT%H:%M:%S.%f"
                        )
                        localized_time = pytz.utc.localize(sync_time).astimezone(tz)
                        last_sync_time = localized_time.strftime(
                            "%Y년 %m월 %d일 %H시 %M분"
                        )
                    except Exception:
                        last_sync_time = connect_last_sync_info
                else:
                    last_sync_time = "알 수 없음"

                if user.created_at:
                    created_at_kr = user.created_at.astimezone(tz)
                    connected_at = created_at_kr.strftime("%Y년 %m월 %d일")
                else:
                    connected_at = "알 수 없음"

                return KakaoResponse(
                    template=Template(
                        outputs=[
                            {
                                "simpleText": SimpleText(
                                    text=f"👤 연결된 가민 프로필 정보\n\n"
                                    f"닉네임: {full_name}\n"
                                    f"이메일: {email}\n"
                                    f"마지막 동기화: {last_sync_time}\n"
                                    f"가민 핏봇 연결일: {connected_at}"
                                )
                            }
                        ]
                    )
                )
            except Exception as e:
                return KakaoResponse(
                    template=Template(
                        outputs=[
                            {
                                "simpleText": SimpleText(
                                    text=f"가민 프로필 정보를 가져오는 데 실패했습니다.\n"
                                    f"가민 커넥트 계정 연결을 확인해주세요.\n"
                                    f"오류: {str(e)}"
                                )
                            }
                        ]
                    )
                )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    async def parse_date_validation(
        self, request: DateParserRequest
    ) -> DateParserResponse:
        """
        챗봇 오픈빌더에서 자연어 기반 날짜 파싱 요청 처리
        """
        origin = (
            request.value.origin
            if request.value and request.value.origin
            else request.utterance
        )
        parsed_date, error_message = await self.date_parser_service.parse_to_date(
            origin
        )

        if error_message:
            return DateParserResponse(status="FAIL", value="", message=error_message)

        return DateParserResponse(
            status="SUCCESS",
            value=str(parsed_date),
            message=str(parsed_date),
        )

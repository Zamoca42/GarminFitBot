from fastapi import APIRouter, Depends

from api.common.schema import KakaoRequest, KakaoResponse
from api.common.schema.date_parser import DateParserRequest, DateParserResponse
from api.v1.kakao.controller import KakaoController
from app.service import DateParserService, TokenService
from core.db import AsyncSession, get_session

router = APIRouter(prefix="/kakao", tags=["카카오 챗봇"])


def get_token_service() -> TokenService:
    return TokenService()


def get_date_parser_service() -> DateParserService:
    return DateParserService()


def get_kakao_controller(
    session: AsyncSession = Depends(get_session),
    token_service: TokenService = Depends(get_token_service),
    date_parser_service: DateParserService = Depends(get_date_parser_service),
) -> KakaoController:
    return KakaoController(session, token_service, date_parser_service)


@router.post("/fit/collection", response_model=KakaoResponse)
async def request_data_collection(
    request: KakaoRequest,
    controller: KakaoController = Depends(get_kakao_controller),
):
    """
    카카오 챗봇에서 데이터 수집 작업 요청
    """
    return await controller.request_data_collection(request)


@router.post("/health/analysis", response_model=KakaoResponse)
async def request_health_analysis(
    request: KakaoRequest,
    controller: KakaoController = Depends(get_kakao_controller),
):
    """
    카카오 챗봇에서 건강 분석 작업 요청
    """
    return await controller.request_health_analysis(request)


@router.post("/profile", response_model=KakaoResponse)
async def get_garmin_profile(
    request: KakaoRequest,
    controller: KakaoController = Depends(get_kakao_controller),
):
    """
    카카오 챗봇에서 연결된 가민 프로필 정보 조회
    """
    return await controller.get_garmin_profile(request)


@router.post("/parse-date", response_model=DateParserResponse)
async def parse_date(
    request: DateParserRequest,
    controller: KakaoController = Depends(get_kakao_controller),
):
    """
    카카오 챗봇에서 자연어 기반 날짜 파싱 요청 처리
    """
    return await controller.parse_date_validation(request)

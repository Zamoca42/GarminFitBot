from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.authentication import AuthenticationMiddleware

from api.common.schema import ResponseModel
from api.v1.auth.router import router as auth_router
from api.v1.data.router import router as data_router
from api.v1.profile.router import router as profile_router
from app.service import (
    GarminAuthManager,
    GarminStatsService,
    GarminSummaryService,
    GarminTimeSeriesService,
)
from core.config import CORS_ORIGINS
from core.db import engine, get_session, init_db
from core.fastapi.middleware import (
    GarminAuthBackend,
    KakaoBotMiddleware,
    KakaoUserMiddleware,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await engine.dispose()


app = FastAPI(
    title="Garmin Fit API",
    description="가민 피트니스 데이터 조회 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 카카오톡 미들웨어 등록
app.add_middleware(KakaoBotMiddleware)
app.add_middleware(KakaoUserMiddleware)

security = HTTPBearer()


# 헬스체크 응답 모델
class HealthResponse(BaseModel):
    status: str
    db_status: str
    timestamp: datetime


app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(data_router)

app.add_middleware(AuthenticationMiddleware, backend=GarminAuthBackend())


@app.get(
    "/summary/syncTime",
    tags=["요약 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="마지막 동기화 시간",
    description="마지막 동기화 시간을 조회합니다",
    dependencies=[Depends(security)],
)
async def get_sync_time(request: Request):
    """마지막 동기화 시간"""
    try:
        summary_service = GarminSummaryService(request.user.garmin_client)
        data = summary_service.get_last_sync_time()
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@app.get(
    "/summary/daily/{date}",
    tags=["요약 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="일일 전체 활동 요약 조회",
    description="특정 날짜의 일일 전체 활동 요약 데이터를 조회합니다",
    dependencies=[Depends(security)],
)
async def get_daily_summary(date: str, request: Request):
    """일일 전체 활동 요약 조회"""
    try:
        summary_service = GarminSummaryService(request.user.garmin_client)
        data = summary_service.get_daily_summary(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@app.get(
    "/summary/sleep/{date}",
    tags=["요약 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="수면 데이터 요약 조회",
    dependencies=[Depends(security)],
)
async def get_sleep_summary(date: str, request: Request):
    """수면 데이터 요약 조회"""
    try:
        summary_service = GarminSummaryService(request.user.garmin_client)
        data = summary_service.get_sleep_summary(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@app.get(
    "/summary/activities",
    tags=["요약 데이터"],
    response_model=ResponseModel,
    summary="활동 목록 요약 조회",
    dependencies=[Depends(security)],
)
async def get_activities(request: Request, limit: int = 20, start: int = 0):
    """활동 목록 요약 조회"""
    try:
        summary_service = GarminSummaryService(request.user.garmin_client)
        data = summary_service.get_activities(limit, start)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@app.get(
    "/summary/sleep-hrv/{date}",
    tags=["요약 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="수면 HRV 요약 조회",
    dependencies=[Depends(security)],
)
async def get_sleep_hrv(date: str, request: Request):
    """수면 HRV 요약 조회"""
    try:
        summary_service = GarminSummaryService(request.user.garmin_client)
        data = summary_service.get_sleep_hrv_summary(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@app.get(
    "/time-series/heart-rates/{date}",
    tags=["시계열 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="심박수 시계열 데이터 조회",
    dependencies=[Depends(security)],
)
async def get_heart_rates(date: str, request: Request):
    """심박수 시계열 데이터 조회"""
    try:
        time_series_service = GarminTimeSeriesService(request.user.garmin_client)
        data = time_series_service.get_heart_rates(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@app.get(
    "/time-series/stress/{date}",
    tags=["시계열 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="스트레스 시계열 데이터 조회",
    dependencies=[Depends(security)],
)
async def get_stress_rates(date: str, request: Request):
    """스트레스 시계열 데이터 조회"""
    try:
        time_series_service = GarminTimeSeriesService(request.user.garmin_client)
        data = time_series_service.get_stress_rates(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@app.get(
    "/time-series/steps/{date}",
    tags=["시계열 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="걸음수 시계열 데이터 조회",
    dependencies=[Depends(security)],
)
async def get_steps_rates(date: str, request: Request):
    """걸음수 시계열 데이터 조회"""
    try:
        time_series_service = GarminTimeSeriesService(request.user.garmin_client)
        data = time_series_service.get_steps_rates(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@app.get(
    "/time-series/sleep-movement/{date}",
    tags=["시계열 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="수면 중 움직임 시계열 데이터 조회",
)
async def get_sleep_movement(date: str, credentials=Depends(security)):
    """수면 중 움직임 시계열 데이터 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)

        time_series_service = GarminTimeSeriesService(client)
        data = time_series_service.get_sleep_movement(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@app.get(
    "/time-series/sleep-hrv/{date}",
    tags=["시계열 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="수면 HRV 시계열 데이터 조회",
)
async def get_sleep_hrv_readings(date: str, credentials=Depends(security)):
    """수면 HRV 시계열 데이터 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)

        time_series_service = GarminTimeSeriesService(client)
        data = time_series_service.get_sleep_hrv(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@app.get(
    "/stats/sleep-quality",
    tags=["통계 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="수면 품질 통계 조회",
)
async def get_sleep_quality_stats(
    end_date: str = None, days: int = 7, credentials=Depends(security)
):
    """수면 품질 통계 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)

        stats_service = GarminStatsService(client)
        data = await stats_service.get_sleep_quality_stats(end_date, days)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 기간의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@app.get(
    "/stats/daily-stress",
    tags=["통계 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="일간 스트레스 통계 조회",
)
async def get_daily_stress_stats(
    end_date: str = None, days: int = 7, credentials=Depends(security)
):
    """일간 스트레스 통계 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)

        stats_service = GarminStatsService(client)
        data = await stats_service.get_daily_stress_stats(end_date, days)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 기간의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@app.get(
    "/stats/weekly-stress",
    tags=["통계 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="주간 스트레스 통계 조회",
)
async def get_weekly_stress_stats(
    end_date: str = None, weeks: int = 4, credentials=Depends(security)
):
    """주간 스트레스 통계 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)

        stats_service = GarminStatsService(client)
        data = await stats_service.get_weekly_stress_stats(end_date, weeks)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 기간의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@app.get(
    "/stats/daily-hrv",
    tags=["통계 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="일간 수면 중 HRV 통계 조회",
)
async def get_daily_hrv_stats(
    end_date: str = None, days: int = 7, credentials=Depends(security)
):
    """일간 수면 중 HRV 통계 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)

        stats_service = GarminStatsService(client)
        data = await stats_service.get_daily_hrv_stats(end_date, days)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 기간의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@app.get(
    "/stats/daily-steps",
    tags=["통계 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="일간 걸음 수 통계 조회",
)
async def get_daily_steps_stats(
    end_date: str = None, days: int = 7, credentials=Depends(security)
):
    """일간 걸음 수 통계 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)

        stats_service = GarminStatsService(client)
        data = await stats_service.get_daily_steps_stats(end_date, days)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 기간의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@app.get(
    "/health",
    tags=["시스템"],
    response_model=HealthResponse,
    summary="시스템 헬스 체크",
)
async def health_check(db: AsyncSession = Depends(get_session)):
    """
    시스템 상태 확인
    - API 서버 상태
    - 데이터베이스 연결 상태
    """
    try:
        # DB 연결 테스트
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "running",
        "db_status": db_status,
        "timestamp": datetime.now(timezone.utc),
    }

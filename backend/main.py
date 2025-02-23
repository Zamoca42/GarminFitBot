from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from db.model.user import User
from db.session import get_session, init_db, engine
from service.auth_manager import GarminAuthManager
from service.summary_service import GarminSummaryService
from service.time_series_service import GarminTimeSeriesService
from service.stats_service import GarminStatsService
from typing import Annotated, Optional, Any
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await engine.dispose()

SessionDep = Annotated[AsyncSession, Depends(get_session)]

app = FastAPI(
    title="Garmin Fit API",
    description="가민 피트니스 데이터 조회 API",
    version="1.0.0",
    lifespan=lifespan
)
security = HTTPBearer()

class LoginRequest(BaseModel):
    email: str
    password: str

class MFARequest(BaseModel):
    email: str
    client_state: dict
    mfa_code: str

class RefreshRequest(BaseModel):
    oauth1_token: dict

# Response 모델 정의
class ResponseModel(BaseModel):
    message: str
    data: Optional[Any] = None

# 헬스체크 응답 모델
class HealthResponse(BaseModel):
    status: str
    db_status: str
    timestamp: datetime

@app.post(
    "/auth/login",
    tags=["인증"],
    response_model=ResponseModel,
    summary="가민 계정 로그인"
)
async def login(
    db: SessionDep,
    request: LoginRequest,
):
    """가민 계정으로 로그인"""
    try:
        garmin_manager = GarminAuthManager()
        client = await garmin_manager.login(request.email, request.password)
        
        if isinstance(client, dict):
            return {
                "message": "MFA 필요",
                "data": client
            }

        await garmin_manager.save_login_user(client, db)
        access_token = garmin_manager.create_login_user_token(client)
        return {
            "message": "로그인 성공",
            "data": {
                "accessToken": access_token
            }
        }

    except Exception as e:
        print(f"Login error: {e}")  # 전체 로그인 프로세스 에러
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    
@app.post(
    "/auth/refresh",
    tags=["인증"],
    response_model=ResponseModel,
    summary="토큰 갱신"
)
async def refresh_token(credentials = Depends(security)):
    """토큰 갱신"""
    try:
        garmin_manager = GarminAuthManager()
        user_info = garmin_manager.get_token_user_info(credentials.credentials)
        client = garmin_manager.refresh_client_from_token(user_info["oauth1Token"])
        access_token = garmin_manager.create_login_user_token(client)
        
        return {
            "message": "토큰 갱신 성공",
            "data": {
                "accessToken": access_token,
                "tokenType": "bearer"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@app.get(
    "/profile",
    tags=["프로필"],
    response_model=ResponseModel,
    summary="사용자 프로필 조회"
)
async def get_user_profile(credentials = Depends(security)):
    """사용자 프로필 조회"""
    try:
        garmin_manager = GarminAuthManager()
        client = garmin_manager.refresh_client_from_token(
           credentials.credentials
        )
        
        return {
            "message": "프로필 조회 성공",
            "data": client.user_profile
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    
@app.get(
    "/profile/db",
    tags=["프로필"],
    response_model=ResponseModel,
    summary="사용자 프로필 조회"
)
async def get_user_profile_db(db: SessionDep):
    """사용자 프로필 조회"""
    try:
        result = await db.get(User, 1)
        print(f"DB user info: {result}")
        await db.commit()
        
        return {
            "message": "프로필 조회 성공",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@app.get(
    "/summary/daily/{date}",
    tags=["요약 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="일일 전체 활동 요약 조회",
    description="특정 날짜의 일일 전체 활동 요약 데이터를 조회합니다"
)
async def get_daily_summary(date: str, credentials = Depends(security)):
    """일일 전체 활동 요약 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)
        
        summary_service = GarminSummaryService(client)
        data = summary_service.get_daily_summary(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다"
            )
        return data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    
@app.get(
    "/summary/sleep/{date}",
    tags=["요약 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="수면 데이터 요약 조회"
)
async def get_sleep_summary(date: str, credentials = Depends(security)):
    """수면 데이터 요약 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)
        summary_service = GarminSummaryService(client)
        data = summary_service.get_sleep_summary(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다"
            )
        return data
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

@app.get(
    "/summary/activities",
    tags=["요약 데이터"],
    response_model=ResponseModel,
    summary="활동 목록 요약 조회"
)
async def get_activities(
    limit: int = 20, 
    start: int = 0, 
    credentials = Depends(security)
):
    """활동 목록 요약 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)
        
        summary_service = GarminSummaryService(client)
        data = summary_service.get_activities(limit, start)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다"
            )
        return data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    
@app.get(
    "/summary/sleep-hrv/{date}",
    tags=["요약 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="수면 HRV 요약 조회"
)
async def get_sleep_hrv(date: str, credentials = Depends(security)):
    """수면 HRV 요약 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)
        summary_service = GarminSummaryService(client)
        data = summary_service.get_sleep_hrv_summary(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다"
            )
        return data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

@app.get(
    "/time-series/heart-rates/{date}",
    tags=["시계열 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="심박수 시계열 데이터 조회"
)
async def get_heart_rates(date: str, credentials = Depends(security)):
    """심박수 시계열 데이터 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)
        
        time_series_service = GarminTimeSeriesService(client)
        data = time_series_service.get_heart_rates(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다"
            )
        return data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

@app.get(
    "/time-series/stress/{date}",
    tags=["시계열 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="스트레스 시계열 데이터 조회"
)
async def get_stress_rates(date: str, credentials = Depends(security)):
    """스트레스 시계열 데이터 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)
        
        time_series_service = GarminTimeSeriesService(client)
        data = time_series_service.get_stress_rates(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다"
            )
        return data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

@app.get(
    "/time-series/steps/{date}",
    tags=["시계열 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="걸음수 시계열 데이터 조회"
)
async def get_steps_rates(date: str, credentials = Depends(security)):
    """걸음수 시계열 데이터 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)
        
        time_series_service = GarminTimeSeriesService(client)
        data = time_series_service.get_steps_rates(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다"
            )
        return data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

@app.get(
    "/time-series/sleep-movement/{date}",
    tags=["시계열 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="수면 중 움직임 시계열 데이터 조회"
)
async def get_sleep_movement(date: str, credentials = Depends(security)):
    """수면 중 움직임 시계열 데이터 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)
        
        time_series_service = GarminTimeSeriesService(client)
        data = time_series_service.get_sleep_movement(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다"
            )
        return data

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

@app.get(
    "/time-series/sleep-hrv/{date}",
    tags=["시계열 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="수면 HRV 시계열 데이터 조회"
)
async def get_sleep_hrv_readings(date: str, credentials = Depends(security)):
    """수면 HRV 시계열 데이터 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)
        
        time_series_service = GarminTimeSeriesService(client)
        data = time_series_service.get_sleep_hrv(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다"
            )
        return data

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

@app.get(
    "/stats/sleep-quality",
    tags=["통계 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="수면 품질 통계 조회"
)
async def get_sleep_quality_stats(
    end_date: str = None,
    days: int = 7,
    credentials = Depends(security)
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
                detail="해당 기간의 데이터가 없습니다"
            )
        return data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

@app.get(
    "/stats/daily-stress",
    tags=["통계 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="일간 스트레스 통계 조회"
)
async def get_daily_stress_stats(
    end_date: str = None, 
    days: int = 7, 
    credentials = Depends(security)
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
                detail="해당 기간의 데이터가 없습니다"
            )
        return data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

@app.get(
    "/stats/weekly-stress",
    tags=["통계 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="주간 스트레스 통계 조회"
)
async def get_weekly_stress_stats(
    end_date: str = None, 
    weeks: int = 4, 
    credentials = Depends(security)
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
                detail="해당 기간의 데이터가 없습니다"
            )
        return data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

@app.get(
    "/stats/daily-hrv",
    tags=["통계 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="일간 수면 중 HRV 통계 조회"
)
async def get_daily_hrv_stats(
    end_date: str = None, 
    days: int = 7, 
    credentials = Depends(security)
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
                detail="해당 기간의 데이터가 없습니다"
            )
        return data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

@app.get(
    "/stats/daily-steps",
    tags=["통계 데이터"],
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="일간 걸음 수 통계 조회"
)
async def get_daily_steps_stats(
    end_date: str = None, 
    days: int = 7, 
    credentials = Depends(security)
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
                detail="해당 기간의 데이터가 없습니다"
            )
        return data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

@app.get(
    "/health",
    tags=["시스템"],
    response_model=HealthResponse,
    summary="시스템 헬스 체크"
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
        "timestamp": datetime.now(timezone.utc)
    }

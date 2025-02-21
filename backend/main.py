import jwt

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from config import SECRET_KEY, ALGORITHM
from service.auth_manager import GarminAuthManager
from service.summary_service import GarminSummaryService
from service.time_series_service import GarminTimeSeriesService
from service.stats_service import GarminStatsService
from fastapi.responses import JSONResponse
from typing import List, Optional, Any

app = FastAPI(
    title="Garmin Fit API",
    description="가민 피트니스 데이터 조회 API",
    version="1.0.0"
)
security = HTTPBearer()

class LoginRequest(BaseModel):
    email: str
    password: str

class MFARequest(BaseModel):
    email: str
    client_state: dict
    mfa_code: str

# Response 모델 정의
class ResponseModel(BaseModel):
    message: str
    data: Optional[Any] = None

@app.post(
    "/auth/login",
    tags=["인증"],
    response_model=ResponseModel,
    summary="가민 계정 로그인"
)
async def login(request: LoginRequest):
    """가민 계정으로 로그인"""
    try:
        garmin_manager = GarminAuthManager()
        result = await garmin_manager.async_login(request.email, request.password)
        
        token_data = {
            "oauth1_token": result["oauth1_token"],
            "oauth2_token": result["oauth2_token"],
            "exp": datetime.now(timezone.utc) + timedelta(days=1)
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        return {
            "access_token": token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@app.post(
    "/auth/mfa",
    tags=["인증"],
    response_model=ResponseModel,
    summary="MFA 코드 확인"
)
async def verify_mfa(request: MFARequest):
    """
    MFA 코드 확인
    TODO: 라이브러리 이슈 수정 후 재구현 필요
    https://github.com/matin/garth/pull/92
    """
    try:
        garmin_manager = GarminAuthManager()
        oauth1, oauth2 = garmin_manager.resume_login(request.client_state, request.mfa_code)
        
        token_data = {
            "oauth1_token": oauth1,
            "oauth2_token": oauth2,
            "exp": datetime.now(timezone.utc) + timedelta(days=1)
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        return {
            "access_token": token,
            "token_type": "bearer"
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
        client = garmin_manager.create_client_from_tokens(
           credentials.credentials
        )
        
        return client.user_profile
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
        client = auth_manager.create_client_from_tokens(credentials.credentials)
        
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
        client = auth_manager.create_client_from_tokens(credentials.credentials)
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
        client = auth_manager.create_client_from_tokens(credentials.credentials)
        
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
        client = auth_manager.create_client_from_tokens(credentials.credentials)
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
        client = auth_manager.create_client_from_tokens(credentials.credentials)
        
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
        client = auth_manager.create_client_from_tokens(credentials.credentials)
        
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
        client = auth_manager.create_client_from_tokens(credentials.credentials)
        
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
        client = auth_manager.create_client_from_tokens(credentials.credentials)
        
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
        client = auth_manager.create_client_from_tokens(credentials.credentials)
        
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
        client = auth_manager.create_client_from_tokens(credentials.credentials)
        
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
        client = auth_manager.create_client_from_tokens(credentials.credentials)
        
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
        client = auth_manager.create_client_from_tokens(credentials.credentials)
        
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
        client = auth_manager.create_client_from_tokens(credentials.credentials)
        
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
        client = auth_manager.create_client_from_tokens(credentials.credentials)
        
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

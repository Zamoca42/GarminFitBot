import jwt

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from services.garmin_api_service import GarminAPIService
from config import SECRET_KEY, ALGORITHM
from services.auth_manager import GarminAuthManager
from services.garmin_data_service import GarminDataService
from typing import Optional, List
from datetime import date

app = FastAPI()
security = HTTPBearer()

class LoginRequest(BaseModel):
    email: str
    password: str

class MFARequest(BaseModel):
    email: str
    client_state: dict
    mfa_code: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/auth/login")
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
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/auth/mfa")
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
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/profile")
async def get_user_profile(credentials = Depends(security)):
    """사용자 프로필 조회"""
    try:
        garmin_manager = GarminAuthManager()
        client = garmin_manager.create_client_from_tokens(
           credentials.credentials
        )
        
        return client.user_profile
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/sleep/details/{date}")
async def get_sleep_details(date: str, credentials = Depends(security)):
    """수면 상세 데이터 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.create_client_from_tokens(credentials.credentials)
        
        data_service = GarminDataService(client)
        return data_service.get_sleep_details(date)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/sleep/stats")
async def get_sleep_stats(
    end_date: Optional[str] = None, 
    days: int = 7, 
    credentials = Depends(security)
):
    """수면 통계 데이터 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.create_client_from_tokens(credentials.credentials)
        
        data_service = GarminDataService(client)
        return data_service.get_sleep_quality_stats(end_date, days)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/stress/daily")
async def get_stress_stats(
    end_date: Optional[str] = None, 
    days: int = 7, 
    credentials = Depends(security)
):
    """일일 스트레스 통계 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.create_client_from_tokens(credentials.credentials)
        
        data_service = GarminDataService(client)
        return data_service.get_stress_stats(end_date, days)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/stress/weekly")
async def get_weekly_stress_stats(
    end_date: Optional[str] = None, 
    weeks: int = 4, 
    credentials = Depends(security)
):
    """주간 스트레스 통계 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.create_client_from_tokens(credentials.credentials)
        
        data_service = GarminDataService(client)
        return data_service.get_weekly_stress_stats(end_date, weeks)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/hrv/details/{date}")
async def get_hrv_details(date: str, credentials = Depends(security)):
    """수면 중 HRV 상세 데이터 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.create_client_from_tokens(credentials.credentials)
        
        data_service = GarminAPIService(client)
        return data_service.get_sleep_hrv_data(date)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/hrv/stats")
async def get_hrv_stats(
    end_date: Optional[str] = None, 
    days: int = 7, 
    credentials = Depends(security)
):
    """HRV 통계 데이터 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.create_client_from_tokens(credentials.credentials)
        
        data_service = GarminDataService(client)
        return data_service.get_hrv_stats(end_date, days)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/heart-rates/{date}")
async def get_heart_rates(date: str, credentials = Depends(security)):
    """24시간 심박수 데이터 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.create_client_from_tokens(credentials.credentials)
        
        data_service = GarminAPIService(client)
        return data_service.get_heart_rates(date)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    
@app.get("/stress/daily/{date}")
async def get_daily_stress_rates(date: str, credentials = Depends(security)):
    """일일 스트레스 데이터 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.create_client_from_tokens(credentials.credentials)

        data_service = GarminAPIService(client)
        return data_service.get_daily_stress_rates(date)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    
@app.get("/steps/daily/{date}")
async def get_daily_steps(date: str, credentials = Depends(security)):
    """일일 걸음 수 데이터 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.create_client_from_tokens(credentials.credentials)

        data_service = GarminAPIService(client)
        return data_service.get_daily_steps_rates(date)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    
@app.get("/steps/stats")
async def get_daily_steps_stats(
    end_date: Optional[str] = None, 
    days: int = 7, 
    credentials = Depends(security)
):
    """일간 걸음 수 통계 데이터 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.create_client_from_tokens(credentials.credentials)

        data_service = GarminDataService(client)
        return data_service.get_daily_steps_stats(end_date, days)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
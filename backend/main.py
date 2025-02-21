import jwt

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from config import SECRET_KEY, ALGORITHM
from service.auth_manager import GarminAuthManager

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
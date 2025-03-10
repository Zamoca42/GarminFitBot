from typing import Dict, List, Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    garmin_id: str
    password: str
    client_id: str


class KakaoUser(BaseModel):
    id: str
    properties: Dict
    type: str


class KakaoUserRequest(BaseModel):
    block: Dict
    lang: Optional[str]
    params: Dict
    timezone: str
    user: KakaoUser
    utterance: str


class KakaoAction(BaseModel):
    clientExtra: Optional[Dict]
    detailParams: Dict
    id: str
    name: str
    params: Dict


class KakaoRequest(BaseModel):
    action: KakaoAction
    bot: Dict
    contexts: Optional[List]
    intent: Dict
    userRequest: KakaoUserRequest


class KakaoResponse(BaseModel):
    version: str = "2.0"
    template: Dict

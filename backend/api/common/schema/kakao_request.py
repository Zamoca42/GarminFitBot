from typing import Dict, List, Optional

from pydantic import BaseModel


class KakaoUser(BaseModel):
    id: str
    type: str
    properties: Dict


class KakaoBlock(BaseModel):
    id: str
    name: str


class KakaoUserRequest(BaseModel):
    timezone: str
    params: Dict
    block: KakaoBlock
    utterance: str
    lang: Optional[str] = None
    user: KakaoUser


class KakaoIntent(BaseModel):
    id: str
    name: str


class KakaoBot(BaseModel):
    id: str
    name: str


class KakaoAction(BaseModel):
    name: str
    clientExtra: Optional[Dict] = None
    params: Dict
    id: str
    detailParams: Dict


class KakaoRequest(BaseModel):
    intent: KakaoIntent
    userRequest: KakaoUserRequest
    bot: KakaoBot
    action: KakaoAction
    contexts: Optional[List] = None

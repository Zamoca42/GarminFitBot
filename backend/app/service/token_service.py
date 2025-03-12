from datetime import datetime, timedelta, timezone

import jwt
from garth import Client as GarthClient
from garth.auth_tokens import OAuth1Token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.model.temp_token import TempClientToken
from core.config import ALGORITHM, SECRET_KEY


class TokenService:
    """토큰 관리 서비스"""

    @staticmethod
    def decode_token(token: str) -> dict:
        """JWT 토큰 디코드"""
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    @staticmethod
    def create_token(client: GarthClient) -> str:
        """JWT 토큰 생성"""
        user = client.user_profile
        oauth1_token = client.oauth1_token
        payload = {
            "userId": user["profileId"],
            "email": user["userName"],
            "oauth1Token": {
                "oauth_token": oauth1_token.oauth_token,
                "oauth_token_secret": oauth1_token.oauth_token_secret,
            },
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def create_garmin_client(oauth1_token: dict) -> GarthClient:
        """Garmin 클라이언트 생성"""
        client = GarthClient()
        oauth1 = OAuth1Token(**oauth1_token)
        client.configure(oauth1_token=oauth1)
        client.refresh_oauth2()
        return client


class TempTokenService:
    """챗봇 가입용 토큰 관리 서비스"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_signup_token(self, user_key: str) -> str:
        try:
            # 1. 기존 토큰 삭제
            await self.delete_signup_token(user_key)

            # 2. 새 토큰 생성 (10분 유효)
            temp_token = TempClientToken(
                client_id=user_key,
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
            )

            self.session.add(temp_token)
            await self.session.commit()

            return user_key
        except Exception as e:
            await self.session.rollback()
            raise e

    async def verify_signup_token(self, client_id: str) -> bool:
        result = await self.session.execute(
            select(TempClientToken).filter(
                TempClientToken.client_id == client_id,
                TempClientToken.expires_at > datetime.now(timezone.utc),
            )
        )
        token = result.scalar_one_or_none()
        return token is not None

    async def delete_signup_token(self, client_id: str):
        result = await self.session.execute(
            select(TempClientToken).where(TempClientToken.client_id == client_id)
        )
        token = result.scalar_one_or_none()
        if token:
            await self.session.delete(token)
            await self.session.commit()

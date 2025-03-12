from garth import Client as GarthClient
from sqlalchemy import select

from app.model import User
from core.db import AsyncSession


class GarminAuthManager:
    """Garmin 인증 관리"""

    def __init__(self, session: AsyncSession):
        self.garth_client = GarthClient()
        self.session = session

    async def login(self, email: str, password: str) -> GarthClient:
        """웹 로그인"""
        result = self.garth_client.login(email, password, return_on_mfa=True)

        if isinstance(result, dict):
            return {"needsMfa": True, "clientState": result["client_state"]}

        return self.garth_client

    async def get_user_info(self, client: GarthClient):
        """유저 정보 가져오기"""
        result = await self.session.execute(
            select(User).where(User.id == client.user_profile["profileId"])
        )
        return result.scalar_one_or_none()

    async def save_login_user(
        self, client: GarthClient, kakao_client_id: str | None = None
    ):
        """DB에 저장 또는 업데이트"""
        try:
            user_info = await self.get_user_info(client)
            user_data = {
                "email": client.user_profile["userName"],
                "display_name": client.user_profile["displayName"],
                "full_name": client.user_profile["fullName"],
                "oauth_token": str(client.oauth1_token.oauth_token),
                "oauth_token_secret": str(client.oauth1_token.oauth_token_secret),
                "domain": (
                    str(client.oauth1_token.domain)
                    if client.oauth1_token.domain
                    else None
                ),
            }

            if kakao_client_id:
                user_data["kakao_client_id"] = kakao_client_id

            if not user_info:
                user_info = User(id=client.user_profile["profileId"], **user_data)
                self.session.add(user_info)
            else:
                for key, value in user_data.items():
                    setattr(user_info, key, value)

            await self.session.commit()
            return user_info

        except Exception as e:
            await self.session.rollback()
            print(f"Failed to save user: {e}")
            raise

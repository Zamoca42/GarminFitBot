import jwt
from garth import Client as GarthClient
from garth.auth_tokens import OAuth1Token

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

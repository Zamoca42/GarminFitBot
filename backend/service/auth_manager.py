import jwt
import garth

from garth import Client as GarthClient
from garth.utils import asdict
from config import SECRET_KEY, ALGORITHM

class GarminAuthManager:
    """Garmin 인증 관리"""
    def __init__(self):
        self.garth_client = GarthClient()
    
    async def async_login(self, email: str, password: str):
        result = garth.login(email, password, return_on_mfa=True)
        
        if isinstance(result, dict):
            return {
                "needs_mfa": True, 
                "client_state": result['client_state']
            }
        
        return {
            "oauth1_token": asdict(garth.client.oauth1_token),
            "oauth2_token": garth.client.oauth2_token.__dict__
        }
    
    def create_client_from_tokens(self, credentials):
        """토큰으로 Garth 클라이언트 생성"""
        payload = jwt.decode(credentials, SECRET_KEY, algorithms=[ALGORITHM])
        self.garth_client.configure(
            oauth1_token=garth.auth_tokens.OAuth1Token(**payload["oauth1_token"]),
            oauth2_token=garth.auth_tokens.OAuth2Token(**payload["oauth2_token"])
        )
        return self.garth_client
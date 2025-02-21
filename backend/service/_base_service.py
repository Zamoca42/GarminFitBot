import logging
from garth import Client as GarthClient
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class BaseGarminService:
    """Garmin 서비스 공통 기능"""
    def __init__(self, client: GarthClient):
        self.client = client
        self.display_name = client.profile['displayName']

    def _make_request(self, endpoint: str, **kwargs):
        """API 요청 공통 처리"""
        try:
            return self.client.connectapi(endpoint, **kwargs)
        except Exception as e:
            logger.error("API 요청 실패 - Endpoint: %s, Error: %s", endpoint, str(e))
            raise

    def _format_response(self, data: List[Dict[str, Any]] | Dict[str, Any] | None, message: str = "success") -> Dict[str, Any]:
        """API 응답 포맷 통일"""
        return {
            "message": message,
            "data": data
        } 
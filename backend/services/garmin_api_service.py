import logging
from garth import Client as GarthClient
from garth.exc import GarthHTTPError
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GarminAPIService:
    """Garmin Connect API 직접 호출"""
    def __init__(self, client: GarthClient):
        self.client = client
        self.display_name = client.profile['displayName']

    def _make_request(self, endpoint: str, **kwargs):
        """API 요청 공통 처리"""
        try:
            return self.client.connectapi(endpoint, **kwargs)
        except GarthHTTPError as e:
            logger.error(
                "Garmin Connect API 에러 발생 - Endpoint: %s, Params: %s, Error: %s",
                endpoint, kwargs.get('params', {}), str(e)
            )
            raise
        except Exception as e:
            logger.error(
                "예상치 못한 에러 발생 - Endpoint: %s, Error: %s",
                endpoint, str(e)
            )
            raise

    def _format_response(self, data: Any, message: str = "success") -> Dict[str, Any]:
        """API 응답 포맷 통일"""
        return {
            "message": message,
            "data": data
        }

    def get_activities(self, limit: int = 20, start: int = 0) -> Dict[str, Any]:
        """활동 목록 조회"""
        endpoint = "/activitylist-service/activities/search/activities"
        params = {"limit": limit, "start": start}
        
        logger.info("활동 목록 조회 - Limit: %d, Start: %d", limit, start)
        try:
            data = self._make_request(endpoint, params=params)
            return self._format_response(data)
        except Exception as e:
            logger.error("활동 목록 조회 실패 - Error: %s", str(e))
            return self._format_response(None, message="error")

    def get_daily_summary(self, date: str) -> Dict[str, Any]:
        """일일 요약 데이터 조회"""
        endpoint = "/usersummary-service/usersummary/daily"
        params = {"calendarDate": date}
        
        logger.info("일일 요약 조회 - Date: %s", date)
        try:
            data = self._make_request(endpoint, params=params)
            return self._format_response(data)
        except Exception as e:
            logger.error("일일 요약 조회 실패 - Date: %s, Error: %s", date, str(e))
            return self._format_response(None, message="error")

    def get_hydration_data(self, date: str) -> Dict[str, Any]:
        """일일 수분 섭취 데이터 조회"""
        endpoint = f"/usersummary-service/usersummary/hydration/allData/{date}"
        
        logger.info("수분 섭취 데이터 조회 - Date: %s", date)
        try:
            data = self._make_request(endpoint)
            return self._format_response(data)
        except Exception as e:
            logger.error("수분 섭취 데이터 조회 실패 - Date: %s, Error: %s", date, str(e))
            return self._format_response(None, message="error")

    def get_sleep_hrv_data(self, date: str) -> Dict[str, Any]:
        """
        수면 중 HRV 상세 데이터 조회
        TODO: HRV 요약과 readings 분리
        """
        endpoint = f"/hrv-service/hrv/{date}"
        
        logger.info("HRV 데이터 조회 - Date: %s", date)
        try:
            raw_data = self._make_request(endpoint)
            if not raw_data:
                return self._format_response(None, message="데이터가 없습니다")
            
            return self._format_response(raw_data)
        except Exception as e:
            logger.error("HRV 데이터 조회 실패 - Date: %s, Error: %s", date, str(e))
            return self._format_response(None, message="error")

    def get_heart_rates(self, date: str) -> Dict[str, Any]:
        """24시간 심박수 데이터 조회"""
        endpoint = f"/wellness-service/wellness/dailyHeartRate"
        params = {"date": date}
        logger.info("24시간 심박수 데이터 조회 - Date: %s", date)
        try:
            data = self._make_request(endpoint, params=params)
            return self._format_response(data)
        except Exception as e:
            logger.error("심박수 데이터 조회 실패 - Date: %s, Error: %s", date, str(e))
            return self._format_response(None, message="error")

    def get_daily_stress_rates(self, date: str) -> Dict[str, Any]:
        """24시간 스트레스 데이터 조회"""
        endpoint = f"/wellness-service/wellness/dailyStress/{date}"
        
        logger.info("일일 스트레스 데이터 조회 - Date: %s", date)
        try:
            data = self._make_request(endpoint)
            return self._format_response(data)
        except Exception as e:
            logger.error("일일 스트레스 데이터 조회 실패 - Date: %s, Error: %s", date, str(e))
            return self._format_response(None, message="error")

    def get_daily_steps_rates(self, date: str) -> Dict[str, Any]:
        """24시간 걸음 수 데이터 조회"""
        endpoint = f"/wellness-service/wellness/dailySummaryChart/"
        params = {"date": date}
        logger.info("일일 걸음 수 데이터 조회 - Date: %s", date)
        
        try:
            data = self._make_request(endpoint, params=params)
            return self._format_response(data)
        except Exception as e:
            logger.error("일일 걸음 수 데이터 조회 실패 - Date: %s, Error: %s", date, str(e))
            return self._format_response(None, message="error")

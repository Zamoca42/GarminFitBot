import logging
from typing import  Optional

from garth import SleepData
from garth.data.sleep import DailySleepDTO

from ._base_service import BaseGarminService

logger = logging.getLogger(__name__)

class GarminSummaryService(BaseGarminService):
    """
    요약 데이터 조회 서비스
    예시: 2월 18일 수면 데이터 요약

    - 단일 시점/하루 단위의 데이터
    - 원본 데이터의 집계/정리
    - 현재 상태나 결과를 보여줌
    """
    
    def get_daily_summary(self, date: str):
        """
        일일 전체 활동(운동, 수면, 수분, 스트레스) 요약
        
        params:
            date: 조회 일자 (YYYY-MM-DD)
        returns:
            DailySummaryDTO: 일일 전체 활동(운동, 수면, 수분, 스트레스) 요약
        """
        endpoint = "/usersummary-service/usersummary/daily"
        params = {"calendarDate": date}
        
        endpoint_name = "일일 전체 활동(운동, 수면, 수분, 스트레스) 요약"
        logger.info("%s 조회 - Date: %s", endpoint_name, date)
        try:
            data = self._make_request(endpoint, params=params)
            return self._format_response(data)
        except Exception as e:
            logger.error("%s 조회 실패 - Date: %s, Error: %s", endpoint_name, date, str(e))
            return self._format_response(None, message="error")
        
    
    def get_sleep_summary(self, date: str) -> Optional[DailySleepDTO]:
        """
        수면 데이터 요약
        
        params:
            date: 조회 일자 (YYYY-MM-DD)
        returns:
            DailySleepDTO: 수면 데이터 요약
        """
        endpoint_name = "수면 데이터 요약"
        logger.info("%s 조회 - Date: %s", endpoint_name, date)
        try:
            sleep_data = SleepData.get(date, client=self.client)
            if sleep_data:
                return self._format_response(sleep_data.daily_sleep_dto, message="success")
            return self._format_response(None, message="success")
        except Exception as e:
            logger.error("%s 조회 실패 - Date: %s, Error: %s", endpoint_name, date, str(e))
            return self._format_response(None, message="error")
        
    def get_sleep_hrv_summary(self, date: str):
        """
        수면 HRV 요약
        
        TODO: HRV 요약과 readings 분리
        garth.data.hrv.HRVSummary 참고

        params:
            date: 조회 일자 (YYYY-MM-DD)
        returns:
            SleepHRVSummaryDTO: 수면 HRV 요약
        """ 
        endpoint = f"/hrv-service/hrv/{date}"

        endpoint_name = "수면 HRV 요약"
        logger.info("%s 조회 - Date: %s", endpoint_name, date)
        try:
            raw_data = self._make_request(endpoint)
            if not raw_data:
                return self._format_response(None, message="데이터가 없습니다")
            
            return self._format_response(raw_data)
        except Exception as e:
            logger.error("%s 조회 실패 - Date: %s, Error: %s", endpoint_name, date, str(e))
            return self._format_response(None, message="error")
    
    def get_activities(self, limit: int = 20, start: int = 0):
        """
        활동 목록 요약 조회
        예: 각 활동의 핵심 정보 요약
        - 2024-02-18 달리기 30분, 5km
        - 2024-02-17 자전거 1시간, 20km
        - 2024-02-16 수영 45분, 1.5km
        
        params:
            limit: 조회할 활동 수
            start: 시작 인덱스
        returns:
            List[ActivityDTO]: 활동 목록 요약
        """
        endpoint = "/activitylist-service/activities/search/activities"
        params = {"limit": limit, "start": start}

        endpoint_name = "활동 목록 요약"
        logger.info("%s 조회 - Limit: %d, Start: %d", endpoint_name, limit, start)
        try:
            data = self._make_request(endpoint, params=params)
            return self._format_response(data)
        except Exception as e:
            logger.error("%s 조회 실패 - Limit: %d, Start: %d, Error: %s", endpoint_name, limit, start, str(e))
            return self._format_response(None, message="error")
    
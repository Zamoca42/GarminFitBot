import logging

from typing import List, Optional
from garth import SleepData
from garth.data.sleep import SleepMovement
from ._base_service import BaseGarminService

logger = logging.getLogger(__name__)

class GarminTimeSeriesService(BaseGarminService):
    """
    시계열 데이터 조회 서비스
    예시: 2월 18일 00:00 ~ 23:59 사이의 1분/5분 단위 측정 데이터

    - 일정 시간 간격으로 연속적으로 측정된 데이터
    - 시간에 따른 변화를 볼 수 있는 데이터
    - 초, 분 단위로 기록
    """
    
    def get_heart_rates(self, date: str):
        """
        심박수 시계열 데이터

        params:
            date: 조회 일자 (YYYY-MM-DD)
        returns:
            List[HeartRate]: 심박수 시계열 데이터
        raises:
            Exception: 조회 실패 시 예외 발생
        """
        endpoint = f"/wellness-service/wellness/dailyHeartRate"
        params = {"date": date}

        endpoint_name = "심박수 시계열 데이터"
        logger.info("%s 조회 - Date: %s", endpoint_name, date)
        try:
            data = self._make_request(endpoint, params=params)
            return self._format_response(data)
        except Exception as e:
            logger.error("%s 조회 실패 - Date: %s, Error: %s", endpoint_name, date, str(e))
            return self._format_response(None, message="error")
        
    def get_stress_rates(self, date: str):
        """
        스트레스 시계열 데이터

        params:
            date: 조회 일자 (YYYY-MM-DD)
        returns:
            List[StressRate]: 스트레스 시계열 데이터
        raises:
            Exception: 조회 실패 시 예외 발생
        """
        endpoint = f"/wellness-service/wellness/dailyStress/{date}"

        endpoint_name = "스트레스 시계열 데이터"
        logger.info("%s 조회 - Date: %s", endpoint_name, date)
        try:
            data = self._make_request(endpoint)
            return self._format_response(data)
        except Exception as e:
            logger.error("%s 조회 실패 - Date: %s, Error: %s", endpoint_name, date, str(e))
            return self._format_response(None, message="error")

    def get_steps_rates(self, date: str):
        """
        걸음수 시계열 데이터
        
        params:
            date: 조회 일자 (YYYY-MM-DD)
        returns:
            List[StepsRate]: 걸음수 시계열 데이터
        raises:
            Exception: 조회 실패 시 예외 발생
        """ 

        endpoint = f"/wellness-service/wellness/dailySummaryChart/"
        params = {"date": date}

        endpoint_name = "걸음수 시계열 데이터"
        logger.info("%s 조회 - Date: %s", endpoint_name, date)
        
        try:
            data = self._make_request(endpoint, params=params)
            return self._format_response(data)
        except Exception as e:
            logger.error("%s 조회 실패 - Date: %s, Error: %s", endpoint_name, date, str(e))
            return self._format_response(None, message="error")

    def get_sleep_movement(self, date: str) -> Optional[List[SleepMovement]]:
        """
        수면 중 움직임 시계열 데이터
        params:
            date: 조회 일자 (YYYY-MM-DD)
        returns:
            List[SleepMovement]: 수면 중 움직임 시계열 데이터
        raises:
            Exception: 조회 실패 시 예외 발생
        """
        endpoint_name = "수면 움직임 시계열 데이터"
        logger.info("%s 조회 - Date: %s", endpoint_name, date)
        try:
            sleep_data = SleepData.get(date, client=self.client)
            if sleep_data:
                return self._format_response(sleep_data.sleep_movement, message="success")
            return self._format_response(None, message="success")
        except Exception as e:
            logger.error("%s 조회 실패 - Date: %s, Error: %s", endpoint_name, date, str(e))
            return self._format_response(None, message="error")

    def get_sleep_hrv(self, date: str):
        """
        수면 HRV 시계열 데이터

        params:
            date: 조회 일자 (YYYY-MM-DD)
        returns:
            List[SleepHRVReading]: 수면 HRV 시계열 데이터
        raises:
            Exception: 조회 실패 시 예외 발생
        """

        endpoint = f"/hrv-service/hrv/{date}"
        endpoint_name = "수면 HRV 시계열 데이터"
        logger.info("%s 조회 - Date: %s", endpoint_name, date)
        try:
            data = self._make_request(endpoint)
            return self._format_response(data)
        except Exception as e:
            logger.error("%s 조회 실패 - Date: %s, Error: %s", endpoint_name, date, str(e))
            return self._format_response(None, message="error")
        
        
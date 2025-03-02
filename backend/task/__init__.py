"""
Celery 작업 패키지

구성:
- base: 기본 작업 유틸리티
- celery_app: Celery 애플리케이션 설정
- garmin_collector: Garmin 데이터 수집 작업
- partition_manager: 데이터베이스 파티션 관리 작업
"""

from .celery_app import celery_app

__all__ = ["celery_app"] 
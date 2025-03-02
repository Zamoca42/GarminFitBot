import logging
from datetime import datetime, timedelta
from typing import List

from celery import shared_task
from sqlalchemy import select

from app.model import User
from app.service import GarminDataCollectorService, TokenService
from core.db.session import session
from task.base import with_db_context

logger = logging.getLogger(__name__)


@shared_task(name="collect_garmin_data")
@with_db_context
async def collect_garmin_data(days_back: int = 0):
    """
    모든 사용자의 Garmin 데이터 수집
    
    Args:
        days_back: 오늘로부터 며칠 전 데이터를 수집할지 (기본값: 0, 오늘)
    """
    logger.info(f"모든 사용자의 Garmin 데이터 수집 시작 (days_back: {days_back})")
    
    # 수집할 날짜 계산
    target_date = datetime.now().date() - timedelta(days=days_back)
    
    try:
        # 모든 사용자 조회
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        logger.info(f"총 {len(users)}명의 사용자 데이터 수집 예정")
        
        # 각 사용자별 데이터 수집
        for user in users:
            await collect_user_data(user.id, target_date)
            
        logger.info(f"모든 사용자의 {target_date} 데이터 수집 완료")
        return {"status": "success", "date": str(target_date), "users_count": len(users)}
        
    except Exception as e:
        logger.error(f"데이터 수집 중 오류 발생: {str(e)}")
        return {"status": "error", "message": str(e)}


@with_db_context
async def collect_user_data(user_id: int, target_date: datetime.date):
    """
    특정 사용자의 특정 날짜 데이터 수집
    
    Args:
        user_id: 사용자 ID
        target_date: 수집할 날짜
    """
    logger.info(f"사용자 {user_id}의 {target_date} 데이터 수집 시작")
    
    try:
        # 사용자 정보 조회
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"사용자 {user_id}를 찾을 수 없음")
            return
        
        # Garmin 클라이언트 생성
        token_service = TokenService()
        oauth1_token = {
            "oauth_token": user.oauth_token,
            "oauth_token_secret": user.oauth_token_secret,
            "domain": user.domain
        }
        garmin_client = token_service.create_garmin_client(oauth1_token)
        
        # 데이터 수집 서비스 초기화
        collector_service = GarminDataCollectorService(client=garmin_client)
        
        # 데이터 수집 실행
        result = await collector_service.collect_daily_data(user_id, target_date)
        
        logger.info(f"사용자 {user_id}의 {target_date} 데이터 수집 완료")
        return result
        
    except Exception as e:
        logger.error(f"사용자 {user_id}의 데이터 수집 중 오류 발생: {str(e)}")
        raise 
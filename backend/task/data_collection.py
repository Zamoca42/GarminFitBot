from datetime import datetime, timedelta

from app.service import GarminDataCollectorService


async def collect_user_data(user_id: int, days: int = 1):
    """사용자 데이터 수집 배치 작업"""
    collector = GarminDataCollectorService()

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days - 1)

    for single_date in (start_date + timedelta(n) for n in range(days)):
        await collector.collect_daily_data(user_id, single_date)

from datetime import datetime, timedelta

from celery import shared_task
from sqlalchemy import text

from core.db.session import session
from task.base import with_db_context


class TimeSeriesPartitionManager:
    PARTITIONED_TABLES = [
        "heart_rate_readings",
        "stress_readings",
        "steps_intraday",
        "sleep_movement",
        "sleep_hrv_readings",
    ]

    async def create_next_month_partitions(self):
        """모든 시계열 테이블의 다음 달 파티션 생성"""
        next_month = datetime.now() + timedelta(days=32)
        month_start = next_month.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)

        for table in self.PARTITIONED_TABLES:
            partition_name = f"{table}_y{month_start.year}m{month_start.month:02d}"

            sql = f"""
            CREATE TABLE IF NOT EXISTS {partition_name} PARTITION OF {table}
            FOR VALUES FROM ('{month_start.date()}') TO ('{month_end.date()}')
            """
            await session.execute(text(sql))
        
        await session.commit()

    async def create_current_month_partitions(self):
        """모든 시계열 테이블의 현재 달 파티션 생성"""
        current_month = datetime.now()
        month_start = current_month.replace(day=1)
        next_month = (month_start + timedelta(days=32)).replace(day=1)

        for table in self.PARTITIONED_TABLES:
            partition_name = f"{table}_y{month_start.year}m{month_start.month:02d}"

            sql = f"""
            CREATE TABLE IF NOT EXISTS {partition_name} PARTITION OF {table}
            FOR VALUES FROM ('{month_start.date()}') TO ('{next_month.date()}')
            """
            await session.execute(text(sql))
        
        await session.commit()

    async def create_specific_month_partitions(self, year: int, month: int):
        """특정 월의 파티션 생성"""
        month_start = datetime(year, month, 1)
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)

        for table in self.PARTITIONED_TABLES:
            partition_name = f"{table}_y{year}m{month:02d}"

            sql = f"""
            CREATE TABLE IF NOT EXISTS {partition_name} PARTITION OF {table}
            FOR VALUES FROM ('{month_start.date()}') TO ('{next_month.date()}')
            """
            await session.execute(text(sql))
        
        await session.commit()

    async def manage_old_partitions(self, retention_days: int = 365):
        """오래된 파티션 관리"""
        old_date = datetime.now() - timedelta(days=retention_days)

        for table in self.PARTITIONED_TABLES:
            partition_name = f"{table}_y{old_date.year}m{old_date.month:02d}"

            # 오래된 파티션 삭제
            drop_sql = f"DROP TABLE IF EXISTS {partition_name}"
            await session.execute(text(drop_sql))
        
        await session.commit()


@shared_task(name="manage_partitions")
@with_db_context
async def manage_partitions():
    """파티션 관리 작업"""
    manager = TimeSeriesPartitionManager()
    
    # 다음 달 파티션 생성
    await manager.create_next_month_partitions()
    
    # 현재 달 파티션 생성 (없는 경우를 대비)
    await manager.create_current_month_partitions()
    
    # 오래된 파티션 삭제
    await manager.manage_old_partitions()
    
    return {"status": "success", "message": "파티션 관리 완료"}

@with_db_context
async def create_specific_month_partition(year: int, month: int):
    """특정 월의 파티션을 수동으로 생성"""
    manager = TimeSeriesPartitionManager()
    await manager.create_specific_month_partitions(year, month)
    return {"status": "success", "message": f"{year}년 {month}월 파티션 생성 완료"}

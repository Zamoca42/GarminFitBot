from datetime import datetime, timedelta

from sqlalchemy import text


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
            CREATE TABLE {partition_name} PARTITION OF {table}
            FOR VALUES FROM ('{month_start.date()}') TO ('{month_end.date()}')
            """
            await db.execute(text(sql))

    async def manage_old_partitions(self, retention_days: int = 365):
        """오래된 파티션 관리"""
        old_date = datetime.now() - timedelta(days=retention_days)

        for table in self.PARTITIONED_TABLES:
            partition_name = f"{table}_y{old_date.year}m{old_date.month:02d}"

            # 오래된 파티션 삭제
            drop_sql = f"DROP TABLE IF EXISTS {partition_name}"
            await db.execute(text(drop_sql))

    async def schedule_partition_maintenance(self):
        """파티션 관리 스케줄링"""
        # 매월 20일에 다음 달 파티션 생성
        await self.create_next_month_partitions()

        # 매월 1일에 오래된 파티션 삭제
        await self.manage_old_partitions()

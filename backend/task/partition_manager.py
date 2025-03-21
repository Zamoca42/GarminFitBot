from datetime import datetime, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from core.db import DatabaseTask, with_db_context
from core.celery_app import celery_app


class TimeSeriesPartitionManager:
    PARTITIONED_TABLES = [
        "heart_rate_readings",
        "stress_readings",
        "steps_intraday",
        "sleep_movement",
        "sleep_hrv_readings",
    ]

    ALL_TABLES = [
        "users",
        "analytics",
        "activities",
        "heart_rate_daily",
        "heart_rate_readings",
        "sleep_sessions",
        "sleep_movement",
        "sleep_hrv_readings",
        "steps_daily",
        "steps_intraday",
        "stress_daily",
        "stress_readings",
        "temp_client_tokens",
    ]

    def __init__(self, session: Session):
        self.session = session

    def create_next_month_partitions(self):
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
            self.session.execute(text(sql))

        self.session.commit()

    def create_current_month_partitions(self):
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
            self.session.execute(text(sql))

        self.session.commit()

    def create_specific_month_partitions(self, year: int, month: int):
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
            self.session.execute(text(sql))

        self.session.commit()

    def manage_old_partitions(self, retention_days: int = 365):
        """오래된 파티션 관리"""
        old_date = datetime.now() - timedelta(days=retention_days)

        for table in self.PARTITIONED_TABLES:
            partition_name = f"{table}_y{old_date.year}m{old_date.month:02d}"

            # 오래된 파티션 삭제
            drop_sql = f"DROP TABLE IF EXISTS {partition_name}"
            self.session.execute(text(drop_sql))

        self.session.commit()

    def drop_specific_month_partitions(self, year: int, month: int):
        """특정 월의 파티션 제거"""
        for table in self.PARTITIONED_TABLES:
            partition_name = f"{table}_y{year}m{month:02d}"
            drop_sql = f"DROP TABLE IF EXISTS {partition_name}"
            self.session.execute(text(drop_sql))

        self.session.commit()
        return {"status": "success", "message": f"{year}년 {month}월 파티션 삭제 완료"}

    def drop_all_tables(self):
        """모든 테이블 삭제"""
        # 파티션 테이블 먼저 삭제
        for table in self.PARTITIONED_TABLES:
            # 파티션 테이블 조회
            sql = f"""
            SELECT tablename 
            FROM pg_tables 
            WHERE tablename LIKE '{table}_y%'
            """
            result = self.session.execute(text(sql))
            partitions = result.fetchall()

            # 각 파티션 테이블 삭제
            for partition in partitions:
                partition_name = partition[0]
                drop_sql = f"DROP TABLE IF EXISTS {partition_name} CASCADE"
                self.session.execute(text(drop_sql))

        # 메인 테이블 삭제
        for table in self.ALL_TABLES:
            drop_sql = f"DROP TABLE IF EXISTS {table} CASCADE"
            self.session.execute(text(drop_sql))

        self.session.commit()
        return {"status": "success", "message": "모든 테이블 삭제 완료"}


@celery_app.task(name="manage_partitions", base=DatabaseTask, bind=True)
def manage_partitions(self):
    """파티션 관리 작업"""
    manager = TimeSeriesPartitionManager(self.session)

    # 다음 달 파티션 생성
    manager.create_next_month_partitions()

    # 현재 달 파티션 생성 (없는 경우를 대비)
    manager.create_current_month_partitions()

    # 오래된 파티션 삭제
    manager.manage_old_partitions()

    return {"status": "success", "message": "파티션 관리 완료"}


@with_db_context
def create_specific_month_partition(year: int, month: int, session: Session):
    """특정 월의 파티션을 수동으로 생성"""
    manager = TimeSeriesPartitionManager(session)
    manager.create_specific_month_partitions(year, month)
    return {"status": "success", "message": f"{year}년 {month}월 파티션 생성 완료"}


@with_db_context
def drop_specific_month_partition(year: int, month: int, session: Session):
    """특정 월의 파티션을 수동으로 삭제"""
    manager = TimeSeriesPartitionManager(session)
    return manager.drop_specific_month_partitions(year, month)


@with_db_context
def drop_all_tables(session: Session):
    """모든 테이블을 수동으로 삭제"""
    manager = TimeSeriesPartitionManager(session)
    return manager.drop_all_tables()

"""add pg_partman partitioning to time-series tables

Revision ID: b91def08a10f
Revises:
Create Date: 2025-03-28 22:02:39.264256

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b91def08a10f"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop existing tables to remove conflicting partition settings
    op.execute(
        """
        DROP TABLE IF EXISTS heart_rate_readings CASCADE;
        DROP TABLE IF EXISTS sleep_movement CASCADE;
        DROP TABLE IF EXISTS sleep_hrv_readings CASCADE;
        DROP TABLE IF EXISTS steps_intraday CASCADE;
        DROP TABLE IF EXISTS stress_readings CASCADE;

        DROP TABLE IF EXISTS heart_rate_readings_template CASCADE;
        DROP TABLE IF EXISTS sleep_movement_template CASCADE;
        DROP TABLE IF EXISTS sleep_hrv_readings_template CASCADE;
        DROP TABLE IF EXISTS steps_intraday_template CASCADE;
        DROP TABLE IF EXISTS stress_readings_template CASCADE;
    """
    )

    # Recreate partitioned tables
    op.execute(
        """
        CREATE TABLE heart_rate_readings (
            daily_summary_id BIGINT NOT NULL,
            start_time_gmt TIMESTAMPTZ NOT NULL,
            start_time_local TIMESTAMP NOT NULL,
            heart_rate INTEGER,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY (daily_summary_id, created_at, start_time_local)
        ) PARTITION BY RANGE (created_at);

        CREATE TABLE sleep_movement (
            sleep_session_id BIGINT NOT NULL,
            start_time_gmt TIMESTAMPTZ NOT NULL,
            start_time_local TIMESTAMP NOT NULL,
            interval INTEGER,
            activity_level INTEGER,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY (sleep_session_id, created_at, start_time_local)
        ) PARTITION BY RANGE (created_at);

        CREATE TABLE sleep_hrv_readings (
            sleep_session_id BIGINT NOT NULL,
            start_time_gmt TIMESTAMPTZ NOT NULL,
            start_time_local TIMESTAMP NOT NULL,
            hrv_value INTEGER,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY (sleep_session_id, created_at, start_time_local)
        ) PARTITION BY RANGE (created_at);

        CREATE TABLE steps_intraday (
            daily_summary_id BIGINT NOT NULL,
            start_time_gmt TIMESTAMPTZ NOT NULL,
            end_time_gmt TIMESTAMPTZ NOT NULL,
            start_time_local TIMESTAMP NOT NULL,
            end_time_local TIMESTAMP NOT NULL,
            steps INTEGER,
            activity_level VARCHAR(20),
            intensity INTEGER,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY (daily_summary_id, created_at, start_time_local)
        ) PARTITION BY RANGE (created_at);

        CREATE TABLE stress_readings (
            daily_summary_id BIGINT NOT NULL,
            start_time_gmt TIMESTAMPTZ NOT NULL,
            start_time_local TIMESTAMP NOT NULL,
            stress_level INTEGER,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY (daily_summary_id, created_at, start_time_local)
        ) PARTITION BY RANGE (created_at);
    """
    )

    # Recreate template tables
    op.execute(
        """
        CREATE TABLE heart_rate_readings_template (LIKE heart_rate_readings INCLUDING ALL);
        CREATE INDEX ON heart_rate_readings_template (start_time_local);

        CREATE TABLE sleep_movement_template (LIKE sleep_movement INCLUDING ALL);
        CREATE INDEX ON sleep_movement_template (start_time_local);

        CREATE TABLE sleep_hrv_readings_template (LIKE sleep_hrv_readings INCLUDING ALL);
        CREATE INDEX ON sleep_hrv_readings_template (start_time_local);

        CREATE TABLE steps_intraday_template (LIKE steps_intraday INCLUDING ALL);
        CREATE INDEX ON steps_intraday_template (start_time_local);

        CREATE TABLE stress_readings_template (LIKE stress_readings INCLUDING ALL);
        CREATE INDEX ON stress_readings_template (start_time_local);
    """
    )


def downgrade():
    op.execute(
        """
        DROP TABLE IF EXISTS heart_rate_readings_template CASCADE;
        DROP TABLE IF EXISTS sleep_movement_template CASCADE;
        DROP TABLE IF EXISTS sleep_hrv_readings_template CASCADE;
        DROP TABLE IF EXISTS steps_intraday_template CASCADE;
        DROP TABLE IF EXISTS stress_readings_template CASCADE;

        DROP TABLE IF EXISTS heart_rate_readings CASCADE;
        DROP TABLE IF EXISTS sleep_movement CASCADE;
        DROP TABLE IF EXISTS sleep_hrv_readings CASCADE;
        DROP TABLE IF EXISTS steps_intraday CASCADE;
        DROP TABLE IF EXISTS stress_readings CASCADE;

        DELETE FROM cron.job WHERE jobname = 'run_pg_partman_maintenance_monthly';
    """
    )

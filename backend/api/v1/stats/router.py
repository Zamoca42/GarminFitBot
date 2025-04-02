from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from api.common.schema import ResponseModel
from app.service import GarminStatsService, GarminAuthManager

router = APIRouter(prefix="/stats", tags=["테스트 - 통계 데이터"])
security = HTTPBearer()


@router.get(
    "/sleep-quality",
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="수면 품질 통계 조회",
)
async def get_sleep_quality_stats(
    end_date: str = None, days: int = 7, credentials=Depends(security)
):
    """수면 품질 통계 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)

        stats_service = GarminStatsService(client)
        data = await stats_service.get_sleep_quality_stats(end_date, days)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 기간의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@router.get(
    "/daily-stress",
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="일간 스트레스 통계 조회",
)
async def get_daily_stress_stats(
    end_date: str = None, days: int = 7, credentials=Depends(security)
):
    """일간 스트레스 통계 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)

        stats_service = GarminStatsService(client)
        data = await stats_service.get_daily_stress_stats(end_date, days)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 기간의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@router.get(
    "/weekly-stress",
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="주간 스트레스 통계 조회",
)
async def get_weekly_stress_stats(
    end_date: str = None, weeks: int = 4, credentials=Depends(security)
):
    """주간 스트레스 통계 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)

        stats_service = GarminStatsService(client)
        data = await stats_service.get_weekly_stress_stats(end_date, weeks)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 기간의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@router.get(
    "/daily-hrv",
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="일간 수면 중 HRV 통계 조회",
)
async def get_daily_hrv_stats(
    end_date: str = None, days: int = 7, credentials=Depends(security)
):
    """일간 수면 중 HRV 통계 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)

        stats_service = GarminStatsService(client)
        data = await stats_service.get_daily_hrv_stats(end_date, days)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 기간의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@router.get(
    "/daily-steps",
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="일간 걸음 수 통계 조회",
)
async def get_daily_steps_stats(
    end_date: str = None, days: int = 7, credentials=Depends(security)
):
    """일간 걸음 수 통계 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)

        stats_service = GarminStatsService(client)
        data = await stats_service.get_daily_steps_stats(end_date, days)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 기간의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        ) 
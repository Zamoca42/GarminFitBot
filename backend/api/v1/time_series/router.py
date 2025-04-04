from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer

from api.common.schema import ResponseModel
from app.service import GarminAuthManager, GarminTimeSeriesService

router = APIRouter(prefix="/time-series", tags=["테스트 - 시계열 데이터"])
security = HTTPBearer()


@router.get(
    "/heart-rates/{date}",
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="심박수 시계열 데이터 조회",
    dependencies=[Depends(security)],
)
async def get_heart_rates(date: str, request: Request):
    """심박수 시계열 데이터 조회"""
    try:
        time_series_service = GarminTimeSeriesService(request.user.garmin_client)
        data = time_series_service.get_heart_rates(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@router.get(
    "/stress/{date}",
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="스트레스 시계열 데이터 조회",
    dependencies=[Depends(security)],
)
async def get_stress_rates(date: str, request: Request):
    """스트레스 시계열 데이터 조회"""
    try:
        time_series_service = GarminTimeSeriesService(request.user.garmin_client)
        data = time_series_service.get_stress_rates(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@router.get(
    "/steps/{date}",
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="걸음수 시계열 데이터 조회",
    dependencies=[Depends(security)],
)
async def get_steps_rates(date: str, request: Request):
    """걸음수 시계열 데이터 조회"""
    try:
        time_series_service = GarminTimeSeriesService(request.user.garmin_client)
        data = time_series_service.get_steps_rates(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@router.get(
    "/sleep-movement/{date}",
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="수면 중 움직임 시계열 데이터 조회",
)
async def get_sleep_movement(date: str, credentials=Depends(security)):
    """수면 중 움직임 시계열 데이터 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)

        time_series_service = GarminTimeSeriesService(client)
        data = time_series_service.get_sleep_movement(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@router.get(
    "/sleep-hrv/{date}",
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="수면 HRV 시계열 데이터 조회",
)
async def get_sleep_hrv_readings(date: str, credentials=Depends(security)):
    """수면 HRV 시계열 데이터 조회"""
    try:
        auth_manager = GarminAuthManager()
        client = auth_manager.refresh_client_from_token(credentials.credentials)

        time_series_service = GarminTimeSeriesService(client)
        data = time_series_service.get_sleep_hrv(date)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 데이터가 없습니다",
            )
        return data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )

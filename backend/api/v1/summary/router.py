from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer

from api.common.schema import ResponseModel
from app.service import GarminSummaryService

router = APIRouter(prefix="/summary", tags=["테스트 - 요약 데이터"])
security = HTTPBearer()


@router.get(
    "/sync-time",
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="마지막 동기화 시간",
    description="마지막 동기화 시간을 조회합니다",
    dependencies=[Depends(security)],
)
async def get_sync_time(request: Request):
    """마지막 동기화 시간"""
    try:
        summary_service = GarminSummaryService(request.user.garmin_client)
        data = summary_service.get_last_sync_time()
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
    "/daily/{date}",
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="일일 전체 활동 요약 조회",
    description="특정 날짜의 일일 전체 활동 요약 데이터를 조회합니다",
    dependencies=[Depends(security)],
)
async def get_daily_summary(date: str, request: Request):
    """일일 전체 활동 요약 조회"""
    try:
        summary_service = GarminSummaryService(request.user.garmin_client)
        data = summary_service.get_daily_summary(date)
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
    "/sleep/{date}",
    response_model=ResponseModel,
    response_model_exclude_none=True,
    summary="수면 데이터 요약 조회",
    dependencies=[Depends(security)],
)
async def get_sleep_summary(date: str, request: Request):
    """수면 데이터 요약 조회"""
    try:
        summary_service = GarminSummaryService(request.user.garmin_client)
        data = summary_service.get_sleep_summary(date)
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
    "/activities",
    response_model=ResponseModel,
    summary="활동 목록 요약 조회",
    dependencies=[Depends(security)],
)
async def get_activities(request: Request, limit: int = 20, start: int = 0):
    """활동 목록 요약 조회"""
    try:
        summary_service = GarminSummaryService(request.user.garmin_client)
        data = summary_service.get_activities(limit, start)
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
    summary="수면 HRV 요약 조회",
    dependencies=[Depends(security)],
)
async def get_sleep_hrv(date: str, request: Request):
    """수면 HRV 요약 조회"""
    try:
        summary_service = GarminSummaryService(request.user.garmin_client)
        data = summary_service.get_sleep_hrv_summary(date)
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
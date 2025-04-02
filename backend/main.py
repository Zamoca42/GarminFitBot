from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.authentication import AuthenticationMiddleware

from api.v1.auth.router import router as auth_router
from api.v1.kakao.router import router as kakao_router
from api.v1.profile.router import router as profile_router
from api.v1.stats.router import router as stats_router
from api.v1.summary.router import router as summary_router
from api.v1.task.router import router as task_router
from api.v1.time_series.router import router as time_series_router
from core.config import CORS_ORIGINS
from core.db import engine, get_session, init_db
from core.fastapi.middleware import (
    GarminAuthBackend,
    KakaoBotMiddleware,
    KakaoUserMiddleware,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await engine.dispose()


app = FastAPI(
    title="Garmin Fit API",
    description="가민 피트니스 데이터 조회 API",
    version="1.0.0",
    lifespan=lifespan,
)
Instrumentator().instrument(app).expose(app)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 카카오톡 미들웨어 등록 (순서 중요: 봇 검증 -> 유저 검증)
app.add_middleware(KakaoUserMiddleware, session_factory=get_session)
app.add_middleware(KakaoBotMiddleware)

security = HTTPBearer()

# 라우터 등록
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(task_router)
app.include_router(kakao_router)
app.include_router(summary_router)
app.include_router(time_series_router)
app.include_router(stats_router)

app.add_middleware(AuthenticationMiddleware, backend=GarminAuthBackend())

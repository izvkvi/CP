from contextlib import asynccontextmanager

import traceback
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.exc import (
    DBAPIError,
    OperationalError,
    SQLAlchemyError,
    StatementError,
)
from starlette.responses import PlainTextResponse

from app.api.v1 import (
    auth_routers,
    minio_routers,
    shedule_routers,
    user_routers,
    utils_routers,
    tasks_routers
)
from app.core.config import settings
from app.core.database import engine, init_db, shutdown_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(engine)
    yield
    await shutdown_db(engine)


app = FastAPI(title="CP", lifespan=lifespan)

instrumentator = Instrumentator(
    should_group_status_codes=False, should_ignore_untemplated=True
)
instrumentator.instrument(app)

app.state.instrumentator = instrumentator


@app.get("/metrics")
async def metrics(request: Request):
    auth = request.headers.get("Authorization")
    if auth != f"Bearer {settings.METRICS_TOKEN}":
        raise HTTPException(status_code=403, detail="Forbidden")

    instrumentator: Instrumentator = request.app.state.instrumentator
    registry = instrumentator.registry

    from prometheus_client import generate_latest

    return PlainTextResponse(
        generate_latest(registry), media_type="text/plain"
    )


@app.middleware("http")
async def db_exception_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response

    except OperationalError:
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Database is unavailable. Please try again later."
            },
        )

    except DBAPIError as e:
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Database driver error occurred.",
                "error": str(e.__cause__ or e),
            },
        )

    except StatementError as e:
        orig = getattr(e, "orig", None)
        if orig and "greenlet_spawn" in str(orig):
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Async context lost (greenlet_spawn). "
                    "A SQLAlchemy async operation was called "
                    "outside of an async context or after session commit."
                },
            )
        return JSONResponse(
            status_code=500,
            content={"detail": f"Statement error: {str(e)}"},
        )

    except SQLAlchemyError as e:
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Database error occurred.",
                "error": str(e.__cause__ or e),
            },
        )

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
        )


# Роутеры
app.include_router(user_routers.router, prefix="/api/v1")
app.include_router(auth_routers.router, prefix="/api/v1")
app.include_router(minio_routers.router, prefix="/api/v1")
app.include_router(shedule_routers.router, prefix="/api/v1")
app.include_router(utils_routers.router, prefix="/api/v1")
app.include_router(tasks_routers.router, prefix="/api/v1")


import logging
import os
import time
from pathlib import Path

from fastapi import FastAPI, Request

from app_data import get_health_payload, get_person_payload

LOG_DIR = Path("logs")
APP_LOG_FILE = LOG_DIR / "app.log"
ERROR_LOG_FILE = LOG_DIR / "error.log"


def setup_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    if getattr(setup_logging, "_configured", False):
        return

    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    app_handler = logging.FileHandler(APP_LOG_FILE)
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)

    error_handler = logging.FileHandler(ERROR_LOG_FILE)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "watchfiles", "watchfiles.main"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True
        uvicorn_logger.setLevel(logging.WARNING if logger_name.startswith("watchfiles") else logging.INFO)

    setup_logging._configured = True


setup_logging()

logger = logging.getLogger("app")
app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    started_at = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Unhandled error while processing %s %s",
            request.method,
            request.url.path,
        )
        raise

    elapsed_ms = (time.perf_counter() - started_at) * 1000
    logger.info(
        "%s %s -> %s in %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.get("/health")
def health_check():
    return get_health_payload()


@app.get("/person")
def get_person():
    return get_person_payload()


@app.on_event("startup")
async def startup_event():
    logger.info("Application started")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

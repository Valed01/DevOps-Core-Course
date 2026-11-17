# Standard library
import logging
import os
import platform
import socket
from datetime import datetime, timezone

# Third-party
import uvicorn
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette.exceptions import HTTPException as StarletteHTTPException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()

# env
host = os.getenv("HOST", "0.0.0.0")
port = int(os.getenv("PORT", 5000))
debug = os.getenv("DEBUG", "False").lower() == "true"

# service
SERVICE_NAME = "devops-info-service"
SERVICE_VERSION = "1.0.0"

hostname = socket.gethostname()
platform_name = platform.system()
platform_version = platform.version()
architecture = platform.machine()
cpu_count = os.cpu_count()
python_version = platform.python_version()

# runtime
START_TIME = datetime.now(timezone.utc)


def get_uptime():
    delta = datetime.now(timezone.utc) - START_TIME
    seconds = int(delta.total_seconds())
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return {
        "seconds": seconds,
        "human": f"{hours} hours, {minutes} minutes",
    }


def get_endpoints():
    endpoints = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        for method in sorted(route.methods - {"HEAD", "OPTIONS"}):
            endpoints.append({
                "path": route.path,
                "method": method,
                "description": route.description or route.summary or route.name,
            })
    return endpoints


def error_body(request: Request, error: str, message: str) -> dict:
    return {
        "error": error,
        "message": message,
        "path": request.url.path,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# 404
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        body = error_body(request, "Not Found", "Endpoint does not exist")
    else:
        body = error_body(request, "HTTP Error", str(exc.detail))
    return JSONResponse(status_code=exc.status_code, content=body)


# 500
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")
    return JSONResponse(
        status_code=500,
        content=error_body(request, "Internal Server Error", "An unexpected error occurred"),
    )


@app.get("/")
async def root(request: Request):
    """Service and system information"""
    uptime = get_uptime()
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return {
        "service": {
            "name": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "description": "DevOps course info service",
            "framework": "FastAPI",
        },
        "system": {
            "hostname": hostname,
            "platform": platform_name,
            "platform_version": platform_version,
            "architecture": architecture,
            "cpu_count": cpu_count,
            "python_version": python_version,
        },
        "runtime": {
            "uptime_seconds": uptime["seconds"],
            "uptime_human": uptime["human"],
            "current_time": datetime.now(timezone.utc).isoformat(),
            "timezone": "UTC",
        },
        "request": {
            "client_ip": client_ip,
            "user_agent": user_agent,
            "method": request.method,
            "path": request.url.path,
        },
        "endpoints": get_endpoints(),
    }


@app.get("/health")
async def health(response: Response):
    """Health check"""
    uptime = get_uptime()
    response.status_code = status.HTTP_200_OK
    return {
        "status": "OK",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": uptime["seconds"]
    }


if __name__ == "__main__":
    logger.info("Starting %s on %s:%s (debug=%s)", SERVICE_NAME, host, port, debug)
    uvicorn.run("app:app", host=host, port=port, reload=debug)

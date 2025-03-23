from fastapi import FastAPI, HTTPException
from functools import wraps
import asyncio
import httpx

from fastapi import FastAPI, HTTPException, Request, Response
import asyncio
from functools import wraps
from ..exception import TimeoutException
import inspect
from starlette.responses import JSONResponse
import signal
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = FastAPI()

# Remove the middleware and use exception handlers instead
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logging.error(f"Error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

def handle_server_errors(func):
    """
    Decorator to catch internal server errors, print the traceback,
    and return a standardized error response.
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            return {"result": {"status_code": 500, "detail": f"Error processing Call request: {str(e)}"}, "status_code": 500}

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            return {"result": {"status_code": 500, "detail": f"Error processing Call request: {str(e)}"}, "status_code": 500}

    return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

@app.get("/status")
async def get_status():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8086/status")
        if response.status_code == 200:
            return {"status": "Server is running"}
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to reach the server at localhost:8086"
            )

def timeout(seconds: float):
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            def handler(signum, frame):
                raise TimeoutException(f"Function timed out after {seconds} seconds")

            # Set the signal handler and a timeout
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(int(seconds))

            try:
                if inspect.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                return result
            except TimeoutException as e:
                raise HTTPException(
                    status_code=408,
                    detail=str(e)
                )
            finally:
                # Disable the alarm
                signal.alarm(0)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            def handler(signum, frame):
                raise TimeoutException(f"Function timed out after {seconds} seconds")

            # Set the signal handler and a timeout
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(int(seconds))

            try:
                return func(*args, **kwargs)
            except TimeoutException as e:
                raise HTTPException(
                    status_code=408,
                    detail=str(e)
                )
            finally:
                # Disable the alarm
                signal.alarm(0)

        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper
    return decorator
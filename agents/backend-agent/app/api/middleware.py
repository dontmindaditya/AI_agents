"""
API Middleware
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from time import time
import uuid

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        start_time = time()
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Log response
            duration = time() - start_time
            logger.info(
                f"Request {request_id} completed in {duration:.3f}s with status {response.status_code}"
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
        except Exception as e:
            logger.error(f"Request {request_id} failed: {e}")
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for global error handling"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled error: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Internal server error",
                    "detail": str(e)
                }
            )


def setup_middleware(app: FastAPI):
    """Setup all middleware"""
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)
    logger.info("Middleware configured")
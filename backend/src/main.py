"""FastAPI application entry point.

Main application module with CORS configuration, middleware, and router registration.
"""

import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.auth import router as auth_router
from src.api.content import router as content_router
from src.api.health import router as health_router
from src.api.quiz import router as quiz_router
from src.api.rag import router as rag_router
from src.api.user import router as user_router
from src.core.config import settings
from src.core.database import init_db

# Import models to register them with SQLAlchemy metadata
from src.models import Chapter, User  # noqa: F401
from src.models.chat import ChatMessage, ChatSession  # noqa: F401
from src.models.progress import Bookmark, ReadingProgress  # noqa: F401
from src.models.quiz import Question, Quiz, QuizAttempt  # noqa: F401

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    logger.info("Starting Humanoid Robotics Textbook API...")
    await init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down API...")


app = FastAPI(
    title="Humanoid Robotics Textbook API",
    description="Backend API for the AI-native humanoid robotics educational platform",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)


# ==================== Error Handling Middleware ====================


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors.

    Logs the error and returns a sanitized error response.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        f"Unhandled exception [request_id={request_id}]: {type(exc).__name__}: {exc}",
        exc_info=True,
    )

    # Return sanitized error in production
    if settings.debug:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc),
                "type": type(exc).__name__,
                "request_id": request_id,
            },
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred",
            "request_id": request_id,
        },
    )


# ==================== Request Logging Middleware ====================


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Middleware to log all incoming requests and their responses.

    Adds request ID for tracing and logs timing information.
    """
    # Generate unique request ID
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id

    # Log request
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} - Started"
    )

    # Time the request
    start_time = time.time()

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log response
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Completed {response.status_code} in {process_time:.3f}s"
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response

    except Exception as exc:
        process_time = time.time() - start_time
        logger.error(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Failed after {process_time:.3f}s: {exc}"
        )
        raise


# ==================== CORS Middleware ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Root Endpoint ====================


@app.get("/")
async def root():
    """Root endpoint returning API info."""
    return {
        "name": "Humanoid Robotics Textbook API",
        "version": "0.1.0",
        "status": "running",
    }


# ==================== Register API Routers ====================

app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(content_router, prefix="/api")
app.include_router(rag_router, prefix="/api")
app.include_router(quiz_router, prefix="/api")
app.include_router(user_router, prefix="/api")

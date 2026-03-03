"""
Backend Agent System - Main Entry Point
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.routes import api_router
from app.api.middleware import setup_middleware
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("Starting Backend Agent System...")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    
    # Validate configuration
    if not settings.validate_llm_providers():
        logger.warning("⚠️  WARNING: No LLM provider API keys configured!")
        logger.warning("   Please set at least one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY, GOOGLE_API_KEY")
        logger.warning("   Agent functionality will be limited without LLM providers.")
    else:
        logger.info("✓ LLM providers configured")
    
    if not settings.validate_database():
        logger.warning("⚠️  WARNING: Database not configured!")
        logger.warning("   Please set: SUPABASE_URL and SUPABASE_KEY")
        logger.warning("   Task persistence and history will be disabled.")
    else:
        logger.info("✓ Database configured")
    
    yield
    logger.info("Shutting down Backend Agent System...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered backend agent system with LangChain and LangGraph",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup custom middleware
setup_middleware(app)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Backend Agent System API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
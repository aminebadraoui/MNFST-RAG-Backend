"""
FastAPI application entry point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.utils.logger import setup_logging, get_logger
from app.api.v1 import auth, tenants, users, documents, social, chat, chats
from app.middleware.auth import AuthenticationMiddleware
from app.middleware.response_transform import ResponseTransformMiddleware

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting MNFST-RAG Backend API")
    yield
    logger.info("Application shutdown")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-tenant MNFST-RAG application API with role-based access control",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add authentication middleware
app.add_middleware(AuthenticationMiddleware)

# Add response transformation middleware
app.add_middleware(ResponseTransformMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["Tenants"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(social.router, prefix="/api/v1/social-links", tags=["Social"])
app.include_router(chat.router, prefix="/api/v1/sessions", tags=["Chat"])
app.include_router(chats.router, prefix="/api/v1/chats", tags=["Chats"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
"""
Sloth API - Main Application Entry Point

LEARNING NOTE:
This is where FastAPI starts. It:
1. Creates the FastAPI app instance
2. Configures middleware (CORS for frontend access)
3. Includes all the routers (organized API endpoints)
4. Defines the root/health endpoints

Run with: uvicorn app.main:app --reload

TUTORIAL: https://fastapi.tiangolo.com/tutorial/first-steps/
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import meal_plans_router
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.progress import router as progress_router
from app.routers.subscriptions import router as subscriptions_router

settings = get_settings()

# Create the FastAPI app
# LEARNING NOTE:
# - title/description/version appear in the auto-generated docs at /docs
# - This metadata helps anyone using your API understand what it does
app = FastAPI(
    title="Sloth API",
    description="Backend API for the Sloth meal planning SaaS (Faultierdiät)",
    version="0.1.0",
    docs_url="/docs",      # Swagger UI at /docs
    redoc_url="/redoc",    # ReDoc at /redoc
)

# Configure CORS (Cross-Origin Resource Sharing)
# LEARNING NOTE:
# CORS allows your frontend (different domain/port) to call your API.
# Without this, browsers block requests from localhost:5173 to localhost:8000.
#
# In production, you'd restrict allow_origins to your actual domain.
# For development, we allow localhost ports.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative React port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
# LEARNING NOTE:
# Each router handles a group of related endpoints.
# The prefix is added to all routes in that router.
app.include_router(auth_router)  # Auth endpoints: /auth/*
app.include_router(users_router)  # User profile endpoints: /users/*
app.include_router(meal_plans_router)  # Meal plan endpoints: /meal-plans/*
app.include_router(progress_router)  # Weight tracking endpoints: /weight/*
app.include_router(subscriptions_router)  # Subscription endpoints: /subscriptions/*

# Future routers (uncomment as we build them):
# app.include_router(preferences_router)
# app.include_router(grocery_router)


@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - confirms the API is running.

    LEARNING NOTE:
    This is a simple "smoke test" endpoint. If this works,
    the API is at least starting correctly.
    """
    return {
        "message": "Sloth API is running",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.

    LEARNING NOTE:
    Load balancers and deployment platforms (like Railway)
    often ping /health to check if your app is alive.
    """
    return {
        "status": "healthy",
        "environment": settings.environment,
    }

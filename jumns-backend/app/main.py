"""Jumns API — FastAPI application with Mangum Lambda handler."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum

from app.exceptions import (
    AgentUnavailableError,
    RateLimitExceededError,
    ResourceNotFoundError,
    UnauthorizedError,
)

app = FastAPI(title="Jumns API", docs_url=None, redoc_url=None)

# ---------------------------------------------------------------------------
# CORS — allow Flutter app from any origin (restrict in production)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth middleware — validates Cognito JWT, sets request.state.user_id
from app.middleware.auth import CognitoAuthMiddleware

app.add_middleware(CognitoAuthMiddleware)

# ---------------------------------------------------------------------------
# Global exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(ResourceNotFoundError)
async def not_found_handler(_request: Request, exc: ResourceNotFoundError):
    return JSONResponse(status_code=404, content={"error": "Resource not found"})


@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(_request: Request, exc: UnauthorizedError):
    return JSONResponse(status_code=401, content={"error": "Unauthorized"})


@app.exception_handler(RateLimitExceededError)
async def rate_limit_handler(_request: Request, exc: RateLimitExceededError):
    return JSONResponse(
        status_code=429,
        content={"error": "Daily message limit reached. Upgrade to Pro for unlimited messages."},
    )


@app.exception_handler(AgentUnavailableError)
async def agent_unavailable_handler(_request: Request, exc: AgentUnavailableError):
    return JSONResponse(
        status_code=503,
        content={"error": "AI service temporarily unavailable"},
    )


@app.exception_handler(RequestValidationError)
async def validation_handler(_request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"error": str(exc)})


@app.exception_handler(Exception)
async def generic_handler(_request: Request, exc: Exception):
    # Never leak stack traces to the client
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


# ---------------------------------------------------------------------------
# Health check (unauthenticated)
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Route registration — imported lazily so missing deps don't crash on import
# ---------------------------------------------------------------------------

def _register_routes() -> None:
    """Import and register all route modules."""
    from app.routes import (
        access_code,
        chat,
        goals,
        insights,
        memories,
        messages,
        reminders,
        settings,
        skills,
        subscription,
        tasks,
    )

    for router_module in [
        chat,
        messages,
        goals,
        tasks,
        reminders,
        skills,
        settings,
        subscription,
        access_code,
        insights,
        memories,
    ]:
        app.include_router(router_module.router, prefix="/api")


_register_routes()

# ---------------------------------------------------------------------------
# Lambda entry point
# ---------------------------------------------------------------------------

handler = Mangum(app)

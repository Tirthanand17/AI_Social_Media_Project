"""Production-oriented FastAPI entrypoint.

It reuses the complete application from api.main, registers routes added by the
PROJECT_GUIDE completion audit, and applies rate limiting to /api/* traffic.
"""

from api.main import app
from api.completion_routes import router as completion_router
from api.rate_limiter import RateLimitMiddleware

app.include_router(completion_router)
app.add_middleware(RateLimitMiddleware)

__all__ = ["app"]

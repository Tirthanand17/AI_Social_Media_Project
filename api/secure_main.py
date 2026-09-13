"""Production-oriented FastAPI entrypoint.

It reuses the complete application from api.main and adds the rate-limiting
middleware required by the production-hardening phase of PROJECT_GUIDE.md.
"""

from api.main import app
from api.rate_limiter import RateLimitMiddleware

app.add_middleware(RateLimitMiddleware)

__all__ = ["app"]

"""Live frontend entrypoint.

Use this when the browser keeps showing an older frontend. It imports the existing
FastAPI app from api.main, removes older frontend routes, and serves the current
frontend with no-cache headers plus forced CSS/JS cache busting.
"""
import re

from fastapi.responses import HTMLResponse

try:
    from .main import app, FRONTEND_DIR
except ImportError:  # pragma: no cover
    from main import app, FRONTEND_DIR


LIVE_VERSION = "20260619-simple-v5"


def _remove_existing_frontend_routes() -> None:
    blocked_paths = {"/", "/app", "/app/feature-tools"}
    app.router.routes = [
        route for route in app.router.routes
        if getattr(route, "path", None) not in blocked_paths
    ]


def _frontend_html() -> str:
    index_file = FRONTEND_DIR / "index.html"
    html = index_file.read_text(encoding="utf-8")

    # Force latest local assets even when the HTML has a different version string.
    html = re.sub(r'/static/styles\.css\?v=[^"\']+', f'/static/styles.css?v={LIVE_VERSION}', html)
    html = re.sub(r'/static/app\.js\?v=[^"\']+', f'/static/app.js?v={LIVE_VERSION}', html)

    marker = """
    <div style="position:fixed;right:14px;bottom:14px;z-index:9999;background:#1a1200;color:#ffe082;padding:10px 14px;border-radius:999px;font:800 12px Segoe UI,Arial;box-shadow:0 10px 25px rgba(0,0,0,.25)">
      SIMPLE WORKFLOW v5 · backend connected
    </div>
    """
    html = html.replace("<body>", "<body>" + marker, 1)
    return html


def _no_cache_headers() -> dict[str, str]:
    return {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
    }


_remove_existing_frontend_routes()


@app.get("/", response_class=HTMLResponse)
@app.get("/app", response_class=HTMLResponse)
def live_frontend():
    return HTMLResponse(_frontend_html(), headers=_no_cache_headers())

"""Live frontend entrypoint.

Use this when the browser keeps showing an older frontend.
It imports the existing FastAPI app from api.main, removes the old root/app routes,
and serves the uploaded frontend with cache-busted CSS/JS references.
"""
from fastapi.responses import HTMLResponse

try:
    from .main import app, FRONTEND_DIR
except ImportError:  # pragma: no cover
    from main import app, FRONTEND_DIR


LIVE_VERSION = "20260618-live-v4"


def _remove_existing_frontend_routes() -> None:
    blocked_paths = {"/", "/app", "/app/feature-tools"}
    app.router.routes = [
        route for route in app.router.routes
        if getattr(route, "path", None) not in blocked_paths
    ]


def _frontend_html() -> str:
    index_file = FRONTEND_DIR / "index.html"
    html = index_file.read_text(encoding="utf-8")
    html = html.replace("/static/styles.css?v=2.0", f"/static/styles.css?v={LIVE_VERSION}")
    html = html.replace("/static/app.js?v=1.2.1", f"/static/app.js?v={LIVE_VERSION}")

    marker = """
    <div style="position:fixed;right:14px;bottom:14px;z-index:9999;background:#1a1200;color:#ffe082;padding:10px 14px;border-radius:999px;font:800 12px Segoe UI,Arial;box-shadow:0 10px 25px rgba(0,0,0,.25)">
      LIVE FRONTEND v4 · backend connected
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

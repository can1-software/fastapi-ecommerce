from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.modules.auth.presentation.api.router import router as auth_router

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
)


@app.get("/docs", include_in_schema=False)
async def swagger_ui() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{settings.APP_NAME} - Swagger UI",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_oauth2_redirect() -> HTMLResponse:
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_ui() -> HTMLResponse:
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f"{settings.APP_NAME} - ReDoc",
        redoc_js_url="https://unpkg.com/redoc@2/bundles/redoc.standalone.js",
        with_google_fonts=False,
    )


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "ecommerce API",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
    }


app.include_router(auth_router, prefix="/api/v1")

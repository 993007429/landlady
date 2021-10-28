from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.api.routers import api
from .config import DEBUG, VERSION

app = FastAPI(title='landlady', debug=DEBUG, version=VERSION)

app.include_router(api.router, prefix='/api')


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="landlady",
        version="0.9.0",
        description="This is a very custom OpenAPI schema",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if DEBUG:
    try:
        import pydevd_pycharm

        pydevd_pycharm.settrace('127.0.0.1', port=8001, stdoutToServer=True, stderrToServer=True)
    except (ConnectionRefusedError, ModuleNotFoundError):
        pass

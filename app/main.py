from fastapi import FastAPI

from .config import DEBUG, VERSION
from app.api.routers import api

app = FastAPI(title='landlady', debug=DEBUG, version=VERSION)

app.include_router(api.router, prefix='/api')


if DEBUG:
    try:
        import pydevd_pycharm
        pydevd_pycharm.settrace('127.0.0.1', port=8001, stdoutToServer=True, stderrToServer=True)
    except (ConnectionRefusedError, ModuleNotFoundError):
        pass

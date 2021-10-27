import os
import typing

from databases import DatabaseURL
from starlette.config import Config, undefined
from starlette.datastructures import CommaSeparatedStrings

API_PREFIX = "/api"

JWT_TOKEN_PREFIX = "Token"  # noqa: S105
VERSION = "0.0.0"

PRODUCTION = os.environ.get('LANDLADY_PRODUCTION', 'false').upper() == 'TRUE'


class MultiLayerConfig(object):
    def __init__(self, configs):
        self.configs: typing.List[Config] = configs

    def __call__(
            self, key: str, cast: typing.Callable = None, default: typing.Any = undefined
    ) -> typing.Any:
        for cfg in self.configs[::-1]:
            val = cfg(key, cast=cast, default=None)
            if val is not None:
                return val
        return default


configs = [Config(".env")]
if not PRODUCTION:
    configs.append(Config("dev.env"))
config = MultiLayerConfig(configs)

DEBUG: bool = config("DEBUG", cast=bool, default=False)
PYCHARM_DEBUG: bool = config("PYCHARM_DEBUG", cast=bool, default=False)

DATABASE_URL: DatabaseURL = config("DB_CONNECTION", cast=DatabaseURL)
MAX_CONNECTIONS_COUNT: int = config("MAX_CONNECTIONS_COUNT", cast=int, default=10)
MIN_CONNECTIONS_COUNT: int = config("MIN_CONNECTIONS_COUNT", cast=int, default=10)

LOGIN_TOKEN_SECRET = config('LOGIN_TOKEN_SECRET', default='')

BOX_ROOT = config('BOX_ROOT')
OPS_USER = config('OPS_USER', default='ops')
LOGS_PATH = config('LOGS_PATH', default='/data0/logs')

ALLOWED_HOSTS: typing.List[str] = config(
    "ALLOWED_HOSTS",
    cast=CommaSeparatedStrings,
    default="",
)

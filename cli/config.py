import configparser
import os

JWT_TOKEN_PREFIX = "Token"  # noqa: S105

conf = configparser.RawConfigParser()

conf.read(f'{os.getcwd()}/.landlady')

if not conf.sections():
    print('ERROR: config file: .landlady is not found!')
    import sys
    sys.exit()

PROJECT_ID = conf['Credentials']['project_id']
JWT_TOKEN = conf['Credentials']['token']
DEPLOY_ENDPOINT = conf['Credentials']['endpoint']

BACKEND_INCLUDE = conf['Deploy']['backend_include']
FE_DIST = conf['Deploy']['fe_dist']
EXCLUDE_DIRS = conf['Deploy']['exclude_dirs']
EXCLUDE_SUFFIX = conf['Deploy']['exclude_suffix']

DEPLOY_WEWORK_WEBHOOK = conf['Deploy']['webhook']

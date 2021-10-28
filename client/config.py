import configparser
import os

JWT_TOKEN_PREFIX = "Token"  # noqa: S105

conf = configparser.RawConfigParser()

conf.read(f'{os.getcwd()}/.landlady-dev')

if not conf.sections():
    print('ERROR: config file: .landlady is not found!')
    import sys
    sys.exit()

PROJECT_ID = conf['Credentials']['project_id']
JWT_TOKEN = conf['Credentials']['token']
DEPLOY_ENDPOINT = conf['Credentials']['endpoint']
EXCLUDE_FILES = conf['Deploy']['exclude']

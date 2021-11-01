import enum
import os
from typing import Dict, Optional, List

import click
import requests
import sseclient
from prettytable import PrettyTable

from client.config import DEPLOY_ENDPOINT, JWT_TOKEN, PROJECT_ID, JWT_TOKEN_PREFIX, BACKEND_INCLUDE, FE_DIST
from client.packing import make_targz


class BoxOperation(enum.Enum):
    apply = '1'
    apply_fe = '2'
    free = '3'


class CLI(object):
    def __init__(self, box_id: int, command: str, arg1: str, arg2: str, **options):
        self.command = command
        self.box_id = box_id
        self.arg1 = arg1
        self.arg2 = arg2
        self.session = Session()
        self.options = options

    def __call__(self):
        if not self.box_id:
            if self.command == 'list' and not self.arg1:
                self.session.list_box()
            else:
                print('请指定box_id')
                return
        else:
            if self.command == 'deploy':
                force = self.options.get('force', False)
                self.session.deploy_in_box(self.box_id, force=force)
            elif self.command == 'pip':
                self.session.pip_in_box(self.box_id, command=self.arg1, package_name=self.arg2)
            elif self.command == 'free':
                self.session.free_box(self.box_id)
            elif self.command == 'log':
                self.session.fetch_log(self.box_id)
            elif self.command == 'ls':
                self.session.list_files(box_id=self.box_id, path=self.arg1)
            elif self.command == 'cat':
                if not self.arg1:
                    print('请指定要查看的文件名, e.g. box [box id] cat nginx.conf ')
                self.session.show_file(box_id=self.box_id, filename=self.arg1)


class ServerErrorException(Exception):
    def __init__(self, msg=''):
        self.msg = msg


class Session(object):

    def get_headers(self, extra: Optional[Dict[str, str]] = None):
        headers = {'Authorization': f'{JWT_TOKEN_PREFIX} {JWT_TOKEN}'}
        if extra:
            headers.update(extra)
        return headers

    def get_json_response(self, resp) -> dict:
        try:
            result = resp.json()
        except ValueError:
            raise ServerErrorException()

        msg = result.get('detail', '')
        if msg:
            raise ServerErrorException(msg=msg)

        return result

    def list_box(self):
        url = f'{DEPLOY_ENDPOINT}/projects/{PROJECT_ID}/boxes'
        resp = requests.get(url, headers=self.get_headers())
        result = self.get_json_response(resp)

        self.display_boxes(result.get('list', [])[::-1])

    def free_box(self, box_id: int):
        box = self.operate_box(box_id, BoxOperation.free)
        self.display_boxes([box] if box else [])

    def operate_box(self, box_id: int, operation: BoxOperation, force: bool = False) -> dict:
        url = f'{DEPLOY_ENDPOINT}/projects/{PROJECT_ID}/boxes/{box_id}'
        r = requests.put(url, params={'operation': operation.value, 'force': force}, headers=self.get_headers())
        result = self.get_json_response(r)
        box = result.get('box')
        return box

    def deploy_in_box(self, box_id: int, force: bool = False):
        backend_include = BACKEND_INCLUDE.strip() if BACKEND_INCLUDE else ''
        fe_dist = FE_DIST.strip() if FE_DIST else ''
        if backend_include:
            box = self.operate_box(box_id, BoxOperation.apply, force=force)
        if fe_dist:
            box = self.operate_box(box_id, BoxOperation.apply_fe)

        current_dir = os.getcwd()
        bundle_name = box['project']['name']
        fe_bundle_name = box['feDistName']

        bundles = {}

        if backend_include:
            includes = [item.strip() for item in backend_include.split(',')]
            filename = f"{current_dir}/{bundle_name}.tar.gz"
            make_targz(filename, includes=includes)
            bundles['bundle'] = filename

        if fe_dist:
            fe_dist_mapping = {fe_dist: fe_bundle_name}
            filename = f"{current_dir}/{fe_bundle_name}.tar.gz"
            make_targz(filename, includes=[], fe_dist_mapping=fe_dist_mapping)
            bundles['fe_bundle'] = filename

        url = f'{DEPLOY_ENDPOINT}/projects/{PROJECT_ID}/boxes/{box_id}/upload'
        files = {bname: open(fname, 'rb') for bname, fname in bundles.items()}

        r = requests.post(url, files=files, headers=self.get_headers())
        result = self.get_json_response(r)
        upadted_box = result.get('box')

        print('\n\n')
        print(f'box status:')
        self.display_boxes([upadted_box] if upadted_box else [])
        print('\n')
        print(result['status'])

        for _, f in files.items():
            f.close()

    def fetch_log(self, box_id: int):
        url = f'{DEPLOY_ENDPOINT}/projects/{PROJECT_ID}/boxes/{box_id}/app_log?process_num=0'
        events = sseclient.SSEClient(url, headers=self.get_headers())
        for event in events:
            if event and event.event == 'message':
                print(event.data)

    def display_boxes(self, boxes: List[dict]):
        pt = PrettyTable(['box_id', 'endpoint', 'owner', 'fe_owner', 'start_time', 'status'])
        for box in boxes:
            pt.add_row([
                box['id'],
                box['endpoint'],
                (box.get('user') or {}).get('name', ''),
                (box.get('feOwner') or {}).get('name', ''),
                box['startTime'] or '',
                box['status']])
        print(pt)

    def list_files(self, box_id: int, path: str = ''):
        url = f'{DEPLOY_ENDPOINT}/projects/{PROJECT_ID}/boxes/{box_id}/files/list'
        r = requests.get(url, params={'path': path}, headers=self.get_headers())
        result = self.get_json_response(r)
        print(result.get('msg'))

    def show_file(self, box_id: int, filename: str):
        url = f'{DEPLOY_ENDPOINT}/projects/{PROJECT_ID}/boxes/{box_id}/files/content'
        r = requests.get(url, params={'filename': filename}, headers=self.get_headers())
        result = self.get_json_response(r)
        print(result.get('msg'))

    def pip_in_box(self, box_id: int, command: str, package_name: str) -> dict:
        url = f'{DEPLOY_ENDPOINT}/projects/{PROJECT_ID}/boxes/{box_id}/pip'
        r = requests.put(url, params={'command': command, 'package_name': package_name}, headers=self.get_headers())
        result = self.get_json_response(r)
        print(result.get('msg'))


@click.command()
@click.argument('arg1', required=False)
@click.argument('arg2', required=False)
@click.argument('arg3', required=False)
@click.argument('arg4', required=False)
@click.option('--force', default=False)
def main(arg1='', arg2='', arg3='', arg4='', force=False):
    if arg1.isdigit():
        box_id = int(arg1)
        command, _arg1, _arg2 = arg2, arg3, arg4
    else:
        box_id = None
        command, _arg1, _arg2 = arg1, arg2, arg3
    try:
        cli = CLI(box_id, command, _arg1, _arg2, force=force)
        cli()
    except ServerErrorException as e:
        print(e.msg or '服务端错误')
    except ValueError:
        print('参数不合法')


if __name__ == '__main__':
    main()

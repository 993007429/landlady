import enum
import os
from typing import Dict, Optional, List

import click
import requests
import sseclient
from prettytable import PrettyTable

from client.config import DEPLOY_ENDPOINT, JWT_TOKEN, PROJECT_ID, JWT_TOKEN_PREFIX, INCLUDE_FILES, FE_DIST
from client.packing import make_targz


class BoxOperation(enum.Enum):
    apply = '1'
    free = '2'


class CLI(object):
    def __init__(self, box_id: int, command: str, arg: str):
        self.command = command
        self.box_id = box_id
        self.arg = arg
        self.session = Session()

    def __call__(self):
        if not self.box_id:
            if self.command == 'list' and not self.arg:
                self.session.list_box()
            else:
                print('请指定box_id')
                return
        else:
            if self.command == 'deploy':
                self.session.deploy_in_box(self.box_id)
            elif self.command == 'free':
                self.session.free_box(self.box_id)
            elif self.command == 'log':
                self.session.fetch_log(self.box_id)
            elif self.command == 'ls':
                self.session.list_files(box_id=self.box_id, path=self.arg)
            elif self.command == 'cat':
                if not self.arg:
                    print('请指定要查看的文件名, e.g. box [box id] cat nginx.conf ')
                self.session.show_file(box_id=self.box_id, filename=self.arg)


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

        self.display_boxes(result.get('list', []))

    def free_box(self, box_id: int):
        box = self.operate_box(box_id, BoxOperation.free)
        self.display_boxes([box] if box else [])

    def operate_box(self, box_id: int, operation: BoxOperation) -> dict:
        url = f'{DEPLOY_ENDPOINT}/projects/{PROJECT_ID}/boxes/{box_id}'
        r = requests.put(url, params={'operation': operation.value}, headers=self.get_headers())
        result = self.get_json_response(r)
        box = result.get('box')
        return box

    def deploy_in_box(self, box_id: int):
        box = self.operate_box(box_id, BoxOperation.apply)
        current_dir = os.getcwd()
        filename = f"{current_dir}/{box['project']['name']}.tar.gz"

        includes = [item.strip() for item in INCLUDE_FILES.split(',')] if INCLUDE_FILES else []

        fe_dist = FE_DIST.strip() if FE_DIST else ''
        fe_dist_mapping = {}
        if fe_dist:
            fe_deploy_dist = box['feDist']
            fe_dist_mapping = {fe_dist: fe_deploy_dist}

        make_targz(filename, includes=includes, fe_dist_mapping=fe_dist_mapping)

        url = f'{DEPLOY_ENDPOINT}/projects/{PROJECT_ID}/boxes/{box_id}/upload'
        files = {'file': open(filename, 'rb')}
        r = requests.post(url, files=files, headers=self.get_headers())
        result = self.get_json_response(r)
        upadted_box = result.get('box')

        self.display_boxes([upadted_box] if upadted_box else [])
        print(result['status'])

    def fetch_log(self, box_id: int):
        url = f'{DEPLOY_ENDPOINT}/projects/{PROJECT_ID}/boxes/{box_id}/app_log?process_num=0'
        events = sseclient.SSEClient(url, headers=self.get_headers())
        for event in events:
            if event and event.event == 'message':
                print(event.data)

    def display_boxes(self, boxes: List[dict]):
        pt = PrettyTable(['box_id', 'endpoint', '使用人', '开始时间', 'status'])
        for box in boxes:
            pt.add_row([
                box['id'],
                box['endpoint'],
                (box.get('user') or {}).get('name', '空闲'),
                box['startTime'] or '',
                box['status']])
        print(pt)

    def list_files(self, box_id: int, path: str = ''):
        url = f'{DEPLOY_ENDPOINT}/projects/{PROJECT_ID}/boxes/{box_id}/files/list'
        r = requests.get(url, params={'path': path}, headers=self.get_headers())
        print(r.text)

    def show_file(self, box_id: int, filename: str):
        url = f'{DEPLOY_ENDPOINT}/projects/{PROJECT_ID}/boxes/{box_id}/files/content'
        r = requests.get(url, params={'filename': filename}, headers=self.get_headers())
        print(r.text)


@click.command()
@click.argument('arg1', required=False)
@click.argument('arg2', required=False)
@click.argument('arg3', required=False)
def main(arg1='', arg2='', arg3=''):
    if arg1.isdigit():
        box_id = int(arg1)
        command, arg = arg2, arg3
    else:
        box_id = None
        command, arg = arg1, arg2
    try:
        cli = CLI(box_id=box_id, command=command, arg=arg)
        cli()
    except ServerErrorException as e:
        print(e.msg or '服务端错误')
    except ValueError:
        print('参数不合法')


if __name__ == '__main__':
    main()

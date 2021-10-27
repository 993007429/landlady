import os
from typing import Dict, Optional, List

import click
import requests
import sseclient
from prettytable import PrettyTable

from app.config import JWT_TOKEN_PREFIX
from app.domain.services.box import BoxOperation
from client.config import DEPLOY_ENDPOINT, JWT_TOKEN, PROJECT_ID
from client.packing import make_targz


class CLI(object):
    def __init__(self, command: str, arg1: str):
        self.command = command
        self.arg1 = arg1
        self.session = Session()

    def __call__(self):
        if self.command == 'list':
            self.session.list_box()
        elif self.command == 'deploy':
            box_id = self.arg1
            if not box_id:
                print('请指定box_id')
            self.session.deploy_in_box(int(box_id))
        if self.command == 'free':
            box_id = self.arg1
            if not box_id:
                print('请指定box_id')
            self.session.free_box(int(box_id))
        elif self.command == 'log':
            box_id = self.arg1
            if not box_id:
                print('请指定box_id')
            self.session.fetch_log(int(box_id))


class ServerErrorException(Exception):
    def __init__(self, msg=''):
        self.msg = msg


class Session(object):

    def get_headers(self, extra: Optional[Dict[str, str]] = None):
        headers = {'Authorization': f'{JWT_TOKEN_PREFIX} {JWT_TOKEN}'}
        if extra:
            headers.update(extra)
        return headers

    def get_response(self, resp) -> dict:
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
        result = self.get_response(resp)

        self.display_boxs(result.get('list', []))

    def free_box(self, box_id: int):
        box = self.operate_box(box_id, BoxOperation.free)
        self.display_boxs([box] if box else [])

    def operate_box(self, box_id: int, operation: BoxOperation) -> dict:
        url = f'{DEPLOY_ENDPOINT}/projects/{PROJECT_ID}/boxes/{box_id}'
        r = requests.put(url, params={'operation': operation.value}, headers=self.get_headers())
        result = self.get_response(r)
        box = result.get('box')
        return box

    def deploy_in_box(self, box_id: int):
        box = self.operate_box(box_id, BoxOperation.apply)
        project_name = box.get('project', {}).get('name', '')

        current_dir = os.getcwd()
        filename = f'{current_dir}/bundle.tar.gz'
        make_targz(filename, current_dir, project_name)

        url = f'{DEPLOY_ENDPOINT}/projects/{PROJECT_ID}/boxes/{box_id}/upload'
        files = {'file': open(filename, 'rb')}
        r = requests.post(url, files=files, headers=self.get_headers())
        result = self.get_response(r)

        print(result)

    def fetch_log(self, box_id: int):
        url = f'{DEPLOY_ENDPOINT}/projects/{PROJECT_ID}/boxes/{box_id}/app_log?process_num=0'
        headers = self.get_headers({
            'Accept': 'text/event-stream',
        })
        response = requests.get(url, params={'project_id': PROJECT_ID}, stream=True, headers=headers)
        client = sseclient.SSEClient(response)
        for event in client.events():
            if event.event == 'message':
                print(event.data)

    def display_boxs(self, boxes: List[dict]):
        pt = PrettyTable(['box_id', '使用人', '开始时间', 'status'])
        for box in boxes:
            pt.add_row([box['id'], (box.get('user') or {}).get('name', '空闲'), box['startTime'] or '', box['status']])
        print(pt)


@click.command()
@click.argument('command')
@click.argument('arg1', required=False)
def main(command, arg1=None):
    try:
        cli = CLI(command, arg1)
        cli()
    except ServerErrorException as e:
        print(e.msg or '服务端错误')
    except ValueError:
        print('参数不合法')


if __name__ == '__main__':
    main()

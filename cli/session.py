import enum
import os
from typing import Dict, Optional, List

import requests
import sseclient
from prettytable import PrettyTable

from cli.libs.wechat_work.webhook import WechatWorkWebhook
from cli.config import DEPLOY_ENDPOINT, JWT_TOKEN, PROJECT_ID, JWT_TOKEN_PREFIX, BACKEND_INCLUDE, FE_DIST, \
    DEPLOY_WEWORK_WEBHOOK
from cli.exceptions import ServerErrorException
from cli.packaging import make_targz


class BoxOperation(enum.Enum):
    apply = '1'
    apply_fe = '2'
    free = '3'


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
            return {
                'msg': resp.text
            }

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
        box = None
        if backend_include:
            box = self.operate_box(box_id, BoxOperation.apply, force=force)
        if fe_dist:
            box = self.operate_box(box_id, BoxOperation.apply_fe, force=force)

        if not box:
            return

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

    def deploy_uat(self):
        backend_include = BACKEND_INCLUDE.strip() if BACKEND_INCLUDE else ''

        current_dir = os.getcwd()

        bundles = {}

        if backend_include:
            includes = [item.strip() for item in backend_include.split(',')]
            filename = f"{current_dir}/bundle.tar.gz"
            make_targz(filename, includes=includes)
            bundles['bundle'] = filename
        else:
            return

        url = f'{DEPLOY_ENDPOINT}/projects/{PROJECT_ID}/uat/upload'
        files = {bname: open(fname, 'rb') for bname, fname in bundles.items()}

        r = requests.post(url, files=files, headers=self.get_headers())
        result = self.get_json_response(r)

        print(result['status'])

        for _, f in files.items():
            f.close()
            os.remove(f.name)

    def broadcast_uat_deploy(self, project_name: str):
        if DEPLOY_WEWORK_WEBHOOK:
            url = f'{DEPLOY_ENDPOINT}/projects/{PROJECT_ID}'
            resp = requests.get(url, headers=self.get_headers())
            result = self.get_json_response(resp)
            url = result['project']['uatEndpoint']

            lines = os.popen("git log -1").readlines()
            msg = '>' + '>'.join(lines)
            webhook = WechatWorkWebhook(DEPLOY_WEWORK_WEBHOOK)
            md = f'# [{project_name}]UAT自动部署成功\n> 最新提交：\n{msg}\n测试地址：[{url}]({url})'
            webhook.markdown(md)

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

    def pip_in_box(self, box_id: int, command: str, package_name: str):
        url = f'{DEPLOY_ENDPOINT}/projects/{PROJECT_ID}/boxes/{box_id}/pip'
        r = requests.put(url, params={'command': command, 'package_name': package_name}, headers=self.get_headers())
        result = self.get_json_response(r)
        print(result.get('msg'))

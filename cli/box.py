import sys
import os
import enum

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click

from cli.exceptions import ServerErrorException, InvalidCommandException
from cli.session import Session



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
    except InvalidCommandException:
        print('命令不支持')
    except ServerErrorException as e:
        print(e.msg or '服务端错误')
    except ValueError:
        print('参数不合法')


if __name__ == '__main__':
    main()

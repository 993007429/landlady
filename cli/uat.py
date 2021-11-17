import click
from cli.exceptions import InvalidCommandException, ServerErrorException
from cli.session import Session


class UATCLI(object):
    def __init__(self, command: str, arg1: str):
        self.command = command
        self.arg1 = arg1
        self.session = Session()

    def __call__(self):
        if self.command == 'deploy':
            self.session.deploy_uat()
        else:
            raise InvalidCommandException()


@click.command()
@click.argument('arg1', required=False)
@click.argument('arg2', required=False)
def main(arg1='', arg2=''):
    command, _arg = arg1, arg2
    try:
        cli = UATCLI(command, _arg)
        cli()
    except InvalidCommandException:
        print('命令不支持')
    except ServerErrorException as e:
        print(e.msg or '服务端错误')
    except ValueError:
        print('参数不合法')


if __name__ == '__main__':
    main()

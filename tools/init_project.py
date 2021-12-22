# encoding: utf-8
import os
import subprocess
import sys

import click

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.domain.entities.project import ProjectDeployType
from app.domain.services.box import BoxService
from app.domain.services.factory import ServiceFactory
from app.domain.services.project import ProjectService


@click.command()
@click.option("--project_name", prompt="Please give a project name, e.g. seal", help="project name")
@click.option("--deploy_type", default='python', prompt="Please give a deploy type, e.g. python, php, etc.", help="deploy type")
@click.option("--domain", default='spsspro.com', prompt="Please give a domain, e.g. spsspro.com", help="domain")
@click.option("--uat_name", default='test', prompt="Please give a uat name, e.g. test, uat", help="uat name")
@click.option("--port_prefix", default='90', prompt="Please give a port prefix, e.g. 90", help="port prefix")
@click.option("--url_paths", default='api', prompt="Please give the valid paths as nginx location", help="url paths")
@click.option("--run_command", default='python app.py', prompt="Please give a command to run a server", help="run command")
@click.option("--environment_variables", default='', prompt="Please give environment variables. e.g. SEAL_TEST='True'", help="environment variables")
@click.option("--count", default=2, prompt="How many boxes do you want?", help="box count")
def main(project_name, deploy_type, domain, uat_name, port_prefix, url_paths, run_command, environment_variables, count):
    project_service = ServiceFactory.shared_service(ProjectService)
    box_service = ServiceFactory.shared_service(BoxService)

    project = project_service.get_project_by_name(project_name)
    if not project:
        project = project_service.new_project(
            name=project_name, domain=domain, deploy_type=ProjectDeployType(deploy_type), uat_name=uat_name, port_prefix=port_prefix,
            url_paths=url_paths, run_command=run_command, environment_variables=environment_variables)
    if not project:
        print('创建项目失败，可能已存在同名项目')
        return

    port_prefix = project_service.alloc_server_port(project)
    all_boxes = project_service.get_boxes(project_id=project.id, limit=1000)
    for box in all_boxes:
        box_service.delete_box(box.id)

    for _ in range(count):
        box = box_service.new_box(project_id=project.id, user_id=0, port_prefix=port_prefix, numprocs=1)
        port_prefix += 1
        box_service.init_box(box)

    subprocess.call(['sudo', 'supervisorctl', 'update'])


if __name__ == '__main__':
    main()

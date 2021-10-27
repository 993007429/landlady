import subprocess

import click

from app.domain.services.box import BoxService
from app.domain.services.factory import ServiceFactory
from app.domain.services.project import ProjectService


@click.command()
@click.option("--project_name", prompt="Please give a project name, e.g. seal", help="project name")
@click.option("--domain", default='spsspro.com', prompt="Please give a domain, e.g. spsspro.com", help="domain")
@click.option("--uat_name", default='test', prompt="Please give a uat name, e.g. test, uat", help="uat name")
@click.option("--port_prefix", default='90', prompt="Please give a port prefix, e.g. 90", help="port prefix")
@click.option("--url_paths", default='api', prompt="Please give the valid paths as nginx location", help="url paths")
@click.option("--run_command", default='python app.py', prompt="Please give a command to run a server", help="run command")
@click.option("--count", default=2, prompt="How many boxes do you want?", help="box count")
def main(project_name, domain, uat_name, port_prefix, url_paths, run_command, count):
    project_service = ServiceFactory.shared_service(ProjectService)
    box_service = ServiceFactory.shared_service(BoxService)

    project = project_service.get_project_by_name(project_name)
    if not project:
        project = project_service.new_project(
            name=project_name, domain=domain, uat_name=uat_name, port_prefix=port_prefix,
            url_paths=url_paths, run_command=run_command)
    if not project:
        print('创建项目失败，可能已存在同名项目')
        return

    port_prefix = project_service.alloc_server_port(project)
    all_boxes = box_service.get_boxes_by_project(project_id=project.id, limit=1000)
    for box in all_boxes:
        box_service.delete_box(box.id)

    for _ in range(count):
        box = box_service.new_box(project_id=project.id, user_id=0, port_prefix=port_prefix, numprocs=1)
        port_prefix += 1
        box_service.init_box(box)

    subprocess.call(['sudo', 'supervisorctl', 'update'])


if __name__ == '__main__':
    main()

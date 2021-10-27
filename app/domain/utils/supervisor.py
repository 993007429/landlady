import configparser

from app.config import OPS_USER, LOGS_PATH
from app.domain.entities.box import BoxEntity


def gen_supervisor_conf(box: BoxEntity):
    config = configparser.RawConfigParser()
    section = f'program:{box.app_name}'
    config.add_section(section)
    config.set(
        section, 'command',
        f'{box.project.run_command} --port={box.port_prefix}%(process_num)01d')
    config.set(section, 'process_name', f'%(program_name)s-{box.port_prefix}%(process_num)01d')
    config.set(section, 'user', OPS_USER)
    config.set(section, 'directory', box.code_dir)
    config.set(section, 'numprocs', box.numprocs)
    config.set(section, 'numprocs_start', '0')
    config.set(section, 'autostart', 'true')
    config.set(section, 'autorestart', 'true')
    config.set(section, 'stopwaitsecs', '5')
    config.set(section, 'redirect_stderr', 'true')
    config.set(section, 'stdout_logfile', f'{LOGS_PATH}/{box.app_name}/web-{box.port_prefix}%(process_num)01d.log')

    with open(box.supervisor_conf, 'w') as configfile:
        config.write(configfile)

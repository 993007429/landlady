import nginx

from app.domain.entities.box import BoxEntity


def gen_nginx_conf(box: BoxEntity):
    c = nginx.Conf()
    for i in range(box.numprocs):
        port = box.port_prefix + i
        u = nginx.Upstream(f'{box.app_name}-app', nginx.Key('server', f'127.0.0.1:{port}'))
        c.add(u)
    s = nginx.Server()
    s.add(
        nginx.Key('listen', '80'),
        nginx.Key('server_name', f'{box.project.server_name}'),
        nginx.Location(
            '/',
            nginx.Key('add_header', 'Access-Control-Allow-Origin *'),
            nginx.Key('root', f'{box.fe_dir}'),
            nginx.Key('access_log', 'off')
        ),
        nginx.Location(
            f'~ /({"|".join(box.project.url_paths)})',
            nginx.Key('add_header', 'Access-Control-Allow-Origin *'),
            nginx.Key('root', f'{box.fe_dir}'),
            nginx.Key('access_log', 'off')
        ),
    )
    c.add(s)
    nginx.dumpf(c, box.nginx_conf)

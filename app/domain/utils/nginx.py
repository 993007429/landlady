import nginx

from app.domain.entities.box import BoxEntity


def gen_nginx_conf(box: BoxEntity):
    c = nginx.Conf()
    upstream_name = f'{box.app_name}-app'
    for i in range(box.numprocs):
        port = box.port_prefix * 10 + i
        u = nginx.Upstream(upstream_name, nginx.Key('server', f'127.0.0.1:{port}'))
        c.add(u)
    s = nginx.Server()
    s.add(
        nginx.Key('listen', '80'),
        nginx.Key('server_name', f'{box.endpoint}'),
        nginx.Location(
            '/',
            nginx.Key('add_header', 'Access-Control-Allow-Origin *'),
            nginx.Key('root', f'{box.fe_dist_dir}'),
            nginx.Key('access_log', 'off')
        ),
        nginx.Location(
            f'~ /({"|".join(box.project.url_paths)})',
            nginx.Key('add_header', 'X-Frame-Options deny'),
            nginx.Key('add_header', 'Cache-Control no-cache'),
            nginx.Key('add_header', 'X-Content-Type-Options nosniff'),
            nginx.Key('proxy_next_upstream', 'off'),
            nginx.Key('proxy_read_timeout', '240'),
            nginx.Key('proxy_http_version', '1.1'),
            nginx.Key('proxy_redirect', 'off'),
            nginx.Key('proxy_pass', f'http://{upstream_name}'),
        ),
    )
    c.add(s)
    nginx.dumpf(c, box.nginx_conf)

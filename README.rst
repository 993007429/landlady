landlady
=======

landlady是一个轻量化的开发/UAT环境管理系统，在有跳板机的服务器环境下，为开发人员提供一个沙盒，让他们可以完成简单的代码部署。
前端工程师和后端工程师都可使用这个系统进行代码部署。

代码部署不依赖git分支，完全是本地文件的上传，类似rsync

交互界面目前只提供了CLI，目前支持的功能：

- 查看环境列表
- 部署代码到某个环境
- 释放某个环境
- 查看环境里面的文件
- 查看环境部署应用的log

主要依赖
---------------
- Python 3.8+

安装CLI
---------------

推荐使用pip安装（需指定idiaoyan的pip源

::

   $ python -m pip install box --index-url=http://mirrors.idiaoyan.cn/repository/pypi/simple/ --trusted-host=mirrors.idiaoyan.cn

或者你使用源码安装

::

    git checkout git@code.idiaoyan.cn:yu.zhao/landlady.git

    cd landlady & python setup.py install


开始使用
---------------

首先，在你需要部署的项目根目录下面，创建一个配置文件：.landlady

::

    [Credentials]
    endpoint=http://deploy.uat.spsspro.com/api
    token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MzgwMjA3NDUsInVpZCI6MSwibmFt
    project_id=1

    [Deploy]
    backend_include=seal,local_settings,app.py
    fe_dist=dist
    exclude_dirs=.git,local_settings/.git,__pycache__,tests
    exclude_suffix=.pyc,__pycache__


首先这个系统需要在一台uat服务器上面部署，部署好之后，部署人员可以给到你：

- endpoint:    这个服务的api地址
- project_id： 你要部署的项目，在服务器上注册的项目id
- token:       部署人员可以在服务器上为你创建账户，给你这个账户的token

接下来你可以配置你要部署项目了：

- backend_include:  你需要同步到服务器的目录白名单，以逗号分割
- fe_dist:          前端文件所在目录（编译后的文件）
- exclude_dirs:     你需要排除的目录，以逗号分割
- exclude_suffix:   你需要排除的文件后缀，以逗号分割


接下来你可以使用命令了：


- 查看环境列表

::

    > box list

    +--------+------------------------+--------+----------+-----------------------------+--------+
    | box_id |        endpoint        | owner  | fe_owner |          start_time         | status |
    +--------+------------------------+--------+----------+-----------------------------+--------+
    |   1    | test-1.uat.spsspro.com | zhaoyu |          | 2021-11-01T11:28:16.832250Z |   on   |
    |   2    | test-2.uat.spsspro.com | lihuan |          | 2021-10-28T13:21:21.263905Z | error  |
    |   3    | test-3.uat.spsspro.com |        |          |                             |  off   |
    |   4    | test-4.uat.spsspro.com |        |          |                             |  off   |
    |   5    | test-5.uat.spsspro.com |        |          |                             |  off   |
    +--------+------------------------+--------+----------+-----------------------------+--------+


以下假设你要操作的box id是： 1

- 部署代码到某个环境

::

    > box 1 deploy
    ...
    local_settings/README.md
    local_settings/seal_dev.ini
    local_settings/sp-webform
    app.py
    +--------+------------------------+--------+----------+-----------------------------+--------+
    | box_id |        endpoint        | owner  | fe_owner |          start_time         | status |
    +--------+------------------------+--------+----------+-----------------------------+--------+
    |   1    | test-1.uat.spsspro.com | zhaoyu |          | 2021-11-01T11:28:16.832250Z |   on   |
    +--------+------------------------+--------+----------+-----------------------------+--------+

    seal-1:seal-1-9050               RUNNING   pid 12637, uptime 0:00:01


- 查看环境部署应用的log, 相当于tail -f

::

    box 1 log


    [W 211028 22:58:29 web:2239] 401 GET /v1/user (127.0.0.1) 1.35ms

    [W 211028 22:58:40 web:2239] 401 GET /v1/user (127.0.0.1) 0.99ms

    [W 211028 22:58:41 web:2239] 401 GET /v1/user (127.0.0.1) 0.96ms


- 列出环境里面的文件

::

    box 1 ls

    drwxrwxr-x 3 ops ops 4096 Oct 28 21:48 .
    drwxrwxr-x 7 ops ops 4096 Oct 27 18:12 ..
    -rw-rw-r-- 1 ops ops  614 Oct 27 23:16 nginx.conf
    drwxrwxr-x 4 ops ops 4096 Oct 28 21:48 seal
    -rw-rw-r-- 1 ops ops  379 Oct 27 18:12 supervisor.conf


- 查看某个文件

::

    box 1 cat seal/seal/__init__.py

    # encoding: utf-8

    __version__ = '0.90.23'



- 释放某个环境
::

    box 1 free

    +--------+------------------------+-------+----------+-----------------------------+--------+
    | box_id |        endpoint        | owner | fe_owner |          start_time         | status |
    +--------+------------------------+-------+----------+-----------------------------+--------+
    |   1    | test-1.uat.spsspro.com |       |          | 2021-11-01T11:28:16.832250Z |   on   |
    +--------+------------------------+-------+----------+-----------------------------+--------+



服务端部署
---------------

to be continued...

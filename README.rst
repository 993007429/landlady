landlady
=======

landlady是一个轻量化的UAT环境管理系统，在有跳板机的服务器环境下，为开发人员提供一个沙盒，让他们可以完成简单的代码部署。

前端工程师和后端工程师都可使用这个系统进行代码部署。

代码部署不依赖git分支，完全是本地文件的上传，类似rsync

交互界面目前只提供CLI.


主要依赖
---------------
- Python 3.8+

安装CLI
---------------

目前公司没有pypi私有镜像仓库，那么目前只能源码安装

::

    git checkout https://gitlab.dipath.cn/dev/landlady.git

    cd landlady & python setup.py install


开始使用
---------------

首先，在你需要部署的项目根目录下面，创建一个配置文件：.landlady

::

    [Credentials]
    endpoint=http://deploy.uat.dipath.cn/api
    token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MzgwMjA3NDUsInVpZCI6MSwibmFt
    project_id=1

    [Deploy]
    backend_include=cyborg,local_settings,app.py
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


查看box列表
...............

::

    > box list

    +--------+------------------------+--------+----------+-----------------------------+--------+
    | box_id |        endpoint        | owner  | fe_owner |          start_time         | status |
    +--------+------------------------+--------+----------+-----------------------------+--------+
    |   1    | test-1.uat.dipath.cn | zhaoyu |          | 2021-11-01T11:28:16.832250Z |   on   |
    |   2    | test-2.uat.dipath.cn | lihuan |          | 2021-10-28T13:21:21.263905Z | error  |
    |   3    | test-3.uat.dipath.cn |        |          |                             |  off   |
    |   4    | test-4.uat.dipath.cn |        |          |                             |  off   |
    |   5    | test-5.uat.dipath.cn |        |          |                             |  off   |
    +--------+------------------------+--------+----------+-----------------------------+--------+

- box_id: box的id
- endpoint： 服务的地址
- owner: box当前的owner
- fe_owner: box当前的前端owner
- start_time: box启动的时间
- status: box的状态，目前有： on, off, error

以下假设你要操作的box id是： 1


部署代码到某个box
...............

::

    box 1 deploy [--force=True]
    ...
    local_settings/README.md
    local_settings/cyborg_dev.ini
    local_settings/sp-webform
    app.py
    +--------+------------------------+--------+----------+-----------------------------+--------+
    | box_id |        endpoint        | owner  | fe_owner |          start_time         | status |
    +--------+------------------------+--------+----------+-----------------------------+--------+
    |   1    | test-1.uat.dipath.cn | zhaoyu |          | 2021-11-01T11:28:16.832250Z |   on   |
    +--------+------------------------+--------+----------+-----------------------------+--------+

    cyborg-1:cyborg-1-9050               RUNNING   pid 12637, uptime 0:00:01

如果当前环境已被占用，操作会失败，但是如果你使用--force=True, 可以强制部署。
强制部署仅针对无法联系上占用者，但又着急部署的情况，不要把强制部署当成一种常态。

如果是第一次部署这个box，服务会起不来，因为你还没安装依赖

安装依赖
...........

::

    box 1 pip install

注意这个命令要求你的项目根目录下面包含 requirements.txt文件，你可以check一下在.landlady文件中backend_include中，有没有包含这个文件
另外这个命令等待时间会有点长，请耐心等待

当然，你也可以单独安装某个包

::

    box 1 pip install click==8.0.3

依赖安装成功之后，再重新deploy，应该就可以成功启动服务了。
如果还是未能成功，请往下看


查看box部署应用的log
.............................

类似于tail -f

::

    box 1 log


    [W 211028 22:58:29 web:2239] 401 GET /v1/user (127.0.0.1) 1.35ms

    [W 211028 22:58:40 web:2239] 401 GET /v1/user (127.0.0.1) 0.99ms

    [W 211028 22:58:41 web:2239] 401 GET /v1/user (127.0.0.1) 0.96ms


列出box里面的文件
...............

::

    box 1 ls

    drwxrwxr-x 3 ops ops 4096 Oct 28 21:48 .
    drwxrwxr-x 7 ops ops 4096 Oct 27 18:12 ..
    -rw-rw-r-- 1 ops ops  614 Oct 27 23:16 nginx.conf
    drwxrwxr-x 4 ops ops 4096 Oct 28 21:48 cyborg
    -rw-rw-r-- 1 ops ops  379 Oct 27 18:12 supervisor.conf


查看某个文件
...............

::

    box 1 cat cyborg/cyborg/__init__.py

    # encoding: utf-8

    __version__ = '0.90.23'



释放某个box
...............

::

    box 1 free

    +--------+------------------------+-------+----------+-----------------------------+--------+
    | box_id |        endpoint        | owner | fe_owner |          start_time         | status |
    +--------+------------------------+-------+----------+-----------------------------+--------+
    |   1    | test-1.uat.dipath.cn |       |          | 2021-11-01T11:28:16.832250Z |   on   |
    +--------+------------------------+-------+----------+-----------------------------+--------+



服务端部署
---------------

服务端目前只提供源码部署

::

    git clone https://gitlab.dipath.cn/dev/landlady.git & cd landlady

编辑配置文件

::

    cp .env.sample .env
    cat .env
    DEBUG=True
    LOGIN_TOKEN_SECRET=123456
    DB_CONNECTION=sqlite:////data/landlady/landlady.db
    BOX_ROOT=/data/landlady/uat-envs
    OPS_USER=dipath
    LOGS_PATH=/data/logs


然后，你需要一个python 3.8+的环境，通常是virtualenv之类的
假设是 /data/www/venv/landlady
进入这个环境

::

    source /data/www/venv/landlady/bin/activate


安装依赖

::

    pip install -r requirements.txt


执行项目初始化脚本, 你会看到一系列的prompt：

::

    python tools/init_project.py
    Please give a project name, e.g. cyborg: cyborg                                 # 项目名称（初始化之后不可更新）
    Please give a domain, e.g. xxxxxx.com [xxxxxx.com]: uat.xxxxxxx.com             # 基础域名
    Please give a uat name, e.g. test, uat [test]: test                             # uat名称，会和box_id, 基础域名组成最终的服务地址
    Please give a port prefix, e.g. 90 [90]: 90                                     # 端口前缀, 比如前缀是90的话，这个项目下面的第一个box所启动的两个python进程可能是9010，9011，以此类推
    Please give the valid paths as nginx location [api]: api,v1,aipath              # nginx配置中暴露的用作后端服务的path
    Please give a command to run a server [python app.py]: python app.py            # 启动python进程的命令，如果你用 uvicorn的话，这个命令可能是  uvicorn app.main:app
    Please give environment variables. e.g. CYBORG_ENV='test' []: CYBORG_ENV='test' # 你可以设定若干个环境变量，比如在应用中你可能会根据某个环境变量来读取不同的配置文件，你需要把这个环境变量设定在这里
    How many boxes do you want? [2]: 2                                              # 单个box你要启动的python进程数

这些配置，除了项目名称之外，都可以在本地sqlite中修改，当然，推荐使用python接口来修改，可以帮你自动对之前已经生成好的box进行更新，包括它的supervisor和nginx的配置文件等等
后续会提供Admin CLI, 来进行更新操作


初始化完成之后，启动服务：

::

    uvicorn app.main:app

当然，推荐用supervisor启动这个服务。


其他事项
---------------

为了让nginx根据不同的url路由到不同的box，需要在本地hosts文件建立域名和服务器的映射


::
    >: vim /etc/hosts

    ##
    # Host Database
    #
    # localhost is used to configure the loopback interface
    # when the system is booting.  Do not change this entry.

    172.16.1.217    test-1.uat.dipath.cn
    172.16.1.217    test-2.uat.dipath.cn
    172.16.1.217    test-3.uat.dipath.cn
    172.16.1.217    test-4.uat.dipath.cn


这样，你就可以把 deploy.uat.dipath.cn 指向 landlady服务， 而 {uat_name}-{box_id}.uat.dipath.cn 指向某个box提供的服务了

import inspect
import uuid
from datetime import datetime
from importlib import import_module
from logging.handlers import TimedRotatingFileHandler

from flask import current_app

from lesscode_flask import download_func_dict
from lesscode_flask.db import db
from lesscode_flask.export_data.data_download_handler import format_to_table_download, upload_result_url
from lesscode_flask.log.access_log_handler import AccessLogHandler
from lesscode_flask.model.user import User
from lesscode_flask.utils.file.file_utils import check_or_create_dir
from lesscode_flask.utils.swagger.swagger_template import split_doc
from lesscode_flask.utils.swagger.swagger_util import generate_openapi_spec, replace_symbol, get_params_type, \
    get_sample_data


# from flask_login import LoginManager
# from flask_swagger_ui import get_swaggerui_blueprint


def setup_logging(app):
    """
    初始化日志配置
    1. 日志等级
        DEBUG : 10
        INFO：20
        WARN：30
        ERROR：40
        CRITICAL：50
    :return:
    """
    import logging
    import sys
    # 日志配置
    # 日志级别
    LOG_LEVEL = app.config.get("LESSCODE_LOG_LEVEL", "DEBUG")
    # 日志格式
    LOG_FORMAT = app.config.get("LESSCODE_LOG_FORMAT",
                                '[%(asctime)s] [%(levelname)s] [%(name)s:%(module)s:%(lineno)d] [%(message)s]')
    # 输出管道
    LOG_STDOUT = app.config.get("LESSCODE_LOG_STDOUT", True)
    # 日志文件备份数量
    LOG_FILE_BACKUPCOUNT = app.config.get("LESSCODE_LOG_FILE_BACKUPCOUNT", 7)
    # 日志文件分割周期
    LOG_FILE_WHEN = app.config.get("LESSCODE_LOG_LOG_FILE_WHEN", "D")
    # 日志文件存储路径
    LOG_FILE_PATH = check_or_create_dir(app.config.get("LESSCODE_LOG_FILE_PATH", 'logs/lesscode.log'))
    formatter = logging.Formatter(LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger().setLevel(LOG_LEVEL.upper())
    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout if LOG_STDOUT else sys.stderr)
    console_handler.setFormatter(formatter)
    file_handler = logging.handlers.TimedRotatingFileHandler(LOG_FILE_PATH, when=LOG_FILE_WHEN,
                                                             backupCount=LOG_FILE_BACKUPCOUNT)

    file_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)
    logging.getLogger().addHandler(file_handler)
    logging.addLevelName(100, 'ACCESS')

    LESSCODE_ACCESS_LOG_DB = app.config.get("LESSCODE_ACCESS_LOG_DB", 0)
    if LESSCODE_ACCESS_LOG_DB == 1:
        access_log_handler = AccessLogHandler()
        access_log_handler.level = 100
        logging.getLogger().addHandler(access_log_handler)


def setup_blueprint(app, path=None, pkg_name="handlers", blueprint_map={}):
    import os
    from flask import Blueprint
    import inspect
    """
    动态注册Handler模块
    遍历项目指定包内的Handler，将包内module引入。
    :param path: 项目内Handler的文件路径
    :param pkg_name: 引入模块前缀
    """
    if path is None:
        # 项目内Handler的文件路径，使用当前工作目录作为根
        path = os.path.join(os.getcwd(), pkg_name)
    # 首先获取当前目录所有文件及文件夹
    dynamic_handler_names = os.listdir(path)
    for handler_name in dynamic_handler_names:
        # 利用os.path.join()方法获取完整路径
        full_file = os.path.join(path, handler_name)
        # 循环判断每个元素是文件夹还是文件
        if os.path.isdir(full_file) and handler_name != "__pycache__":
            # 文件夹递归遍历
            setup_blueprint(app, os.path.join(path, handler_name), ".".join([pkg_name, handler_name]), blueprint_map)
        elif os.path.isfile(full_file) and handler_name.lower().endswith("handler.py"):
            # 文件，并且为handler结尾，认为是请求处理器，完成动态装载
            module_path = "{}.{}".format(pkg_name, handler_name.replace(".py", ""))
            module = import_module(module_path)  # __import__(module_path)
            for name, obj in inspect.getmembers(module):
                # 找到Blueprint 的属性进行注册
                if isinstance(obj, Blueprint):
                    # 如果有配置统一前缀则作为蓝图路径的统一前缀
                    blueprint_name = obj.name
                    if blueprint_name in blueprint_map:
                        continue
                    else:
                        if hasattr(obj, "url_prefix") and app.config.get("ROUTE_PREFIX", ""):
                            obj.url_prefix = f'{app.config.get("ROUTE_PREFIX")}{obj.url_prefix}'
                        blueprint_map[blueprint_name] = obj
    return blueprint_map


def setup_query_runner():
    """
    注入数据查询执行器
    :return:
    """
    from redash.query_runner import import_query_runners
    from redash import settings as redash_settings
    import_query_runners(redash_settings.QUERY_RUNNERS)


def setup_sql_alchemy(app):
    """
    配置SQLAlchemy
    :param app:
    :return:
    """
    if app.config.get("SQLALCHEMY_BINDS"):  # 确保配置SQLALCHEMY_BINDS才注册SQLAlchemy
        db.init_app(app)


def setup_login_manager(app):
    try:
        flask_login = import_module("flask_login")
    except ImportError as e:
        raise Exception(f"flask_login is not exist,run:pip install Flask-Login==0.6.3")
    login_manager = flask_login.LoginManager(app)
    setattr(app, "login_manager", login_manager)

    @login_manager.request_loader
    def request_loader(request):
        return User.get_user(request)


def setup_swagger(app):
    """
    配置Swagger
    :param app:
    :return:
    """
    SWAGGER_URL = app.config.get("SWAGGER_URL", "")  # 访问 Swagger UI 的 URL
    # API_URL = 'http://127.0.0.1:5001/static/swagger.json'  # Swagger 规范的路径（本地 JSON 文件）
    API_URL = app.config.get("SWAGGER_API_URL", "")  # 接口
    # 创建 Swagger UI 蓝图
    try:
        flask_swagger_ui = import_module("flask_swagger_ui")
    except ImportError as e:
        raise Exception(f"flask_swagger_ui is not exist,run:pip install flask-swagger-ui==4.11.1")
    swagger_ui_blueprint = flask_swagger_ui.get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI 访问路径
        app.config.get("OUTSIDE_SCREEN_IP") + API_URL,  # Swagger 文件路径
        config={  # Swagger UI 配置参数
            'app_name': "Flask-Swagger-UI 示例"
        }
    )
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

    @app.route(API_URL, methods=['GET'])
    def swagger_spec():
        from lesscode_flask import __version__
        swag = generate_openapi_spec(app, is_read_template=True)
        swag['info']['title'] = app.config.get("SWAGGER_NAME", "")
        swag['info']['description'] = app.config.get("SWAGGER_DESCRIPTION", "")
        swag['info']['version'] = app.config.get("SWAGGER_VERSION", __version__)
        return swag


def setup_redis(app):
    redis_conn_list = app.config.get("DATA_SOURCE", [])

    for r in redis_conn_list:
        if r.get("type") == "redis":
            try:
                redis = import_module("redis")
            except ImportError:
                raise Exception(f"redis is not exist,run:pip install redis==5.1.1")
            conn = redis.Redis(host=r.get("host"), port=r.get("port"), db=r.get("db"), password=r.get("password"),
                               decode_responses=True)
            if not hasattr(current_app, "redis_conn_dict"):
                current_app.redis_conn_dict = {}
            if getattr(current_app, "redis_conn_dict").get(r.get("conn_name")):
                raise Exception("Connection {} is repetitive".format(r.get("conn_name")))
            else:
                redis_conn_dict = getattr(current_app, "redis_conn_dict")
                redis_conn_dict.update({
                    r.get("conn_name"): conn
                })
                setattr(current_app, "redis_conn_dict", redis_conn_dict)


def setup_resource_register(app):
    def extract_get_parameters(rule, view_func, param_desc_dict=None):
        if param_desc_dict is None:
            param_desc_dict = {}
        parameters = []
        # 提取查询参数和表单参数
        sig = inspect.signature(view_func)
        for arg, param in sig.parameters.items():
            if arg not in rule.arguments:
                param_info = {
                    "name": arg,
                    "in": "query",
                    "type": "string",
                    "description": param_desc_dict[arg] if param_desc_dict.get(arg) else f"Path parameter {arg}",
                }
                if param.default is inspect.Parameter.empty:
                    param_info["required"] = 1
                    param_info["example"] = get_sample_data(get_params_type(param))
                else:
                    param_info["required"] = 0
                    param_info["default"] = param.default
                    param_info["example"] = param.default
                parameters.append(param_info)
        return parameters

    def extract_post_body(view_func, not_allow_list=None, param_desc_dict=None):
        if param_desc_dict is None:
            param_desc_dict = {}
        param_list = []
        # 提取查询参数和表单参数
        sig = inspect.signature(view_func)
        # 如果_request_type == "json 则是json结构，否则都是form-data结构
        if hasattr(view_func, "_request_type") and view_func._request_type == "urlencoded":
            request_type = "x-www-form-urlencoded"
        elif hasattr(view_func, "_request_type") and view_func._request_type == "form-data":
            request_type = "form-data"
        elif hasattr(view_func, "_request_type") and view_func._request_type == "json-data":
            request_type = "raw"
        else:
            request_type = "raw"
        for arg, param in sig.parameters.items():
            param_info = {
                "name": param.name,
                "type": get_params_type(param),
                "description": param_desc_dict[arg] if param_desc_dict.get(arg) else f"Path parameter {arg}",
                "in": request_type
            }
            # 如果默认值是空，则是必填参数
            if param.default is inspect.Parameter.empty:

                param_info["example"] = get_sample_data(get_params_type(param))
                param_info["required"] = 1
            else:
                param_info["default"] = param.default
                param_info["required"] = 0
                if param.default is not None:
                    param_info["example"] = param.default
                else:
                    param_info["example"] = get_sample_data(get_params_type(param))
            # 如果参数类型是FileStorage 则swagger中format为binary 显示导入文件
            if get_params_type(param) == "FileStorage":
                param_info["format"] = "binary"
            if (not_allow_list and arg not in not_allow_list) or not not_allow_list:
                param_list.append(param_info)

        return param_list

    def extract_path_parameters(rule, param_desc_dict=None):
        if param_desc_dict is None:
            param_desc_dict = {}
        param_list = []
        # 提取路径参数
        for arg in rule.arguments:
            param_list.append({
                "name": arg,
                "in": "path",
                "required": 1,
                "description": param_desc_dict[arg] if param_desc_dict.get(arg) else f"Path parameter {arg}",
                "example": "",
                "default": "",
                "type": "string"
            })
        return param_list

    def convert_to_kebab_case_and_camel_case(input_string):
        # 去掉开头的斜杠
        if input_string.startswith('/'):
            input_string = input_string[1:]
        # 将斜杠替换为下划线
        modified_string = input_string.replace('/', '-')
        # 分割字符串
        parts = modified_string.split('_')
        # 将第一个部分转换为小写，其余部分首字母大写
        camel_case_parts = [parts[0].lower()] + [part.capitalize() for part in parts[1:]]
        # 将所有部分连接成小驼峰格式
        camel_case_string = ''.join(camel_case_parts)
        # 将下划线替换为斜杠
        kebab_case_string = camel_case_string.replace('_', '-')
        return kebab_case_string

    def package_resource(label, symbol, access, type, method="", url="", description="", param_list: list = None):
        """
        :param label: 展示中文名称
        :param symbol: 标识符号
        :param access: 访问权限2：需要权限 1：需要登录 0：游客
        :param type:菜单类型 0：功能分组  1：页面 2：接口 3：前端控件 4：接口池接口
        :param method:post、get
        :param url:接口地址
        :param description:接口描述
        :return:
        """
        symbol = convert_to_kebab_case_and_camel_case(symbol)
        resource = {
            "client_id": current_app.config.get("CLIENT_ID", ""),
            "label": label,
            "symbol": symbol,
            "access": access,
            "type": type,
            "method": method,
            "serial_index": 0,
            "url": url,
            "description": description,
            "is_enable": 1,
            "is_deleted": 0,
            "create_user_id": "-",
            "create_user_name": "-",
            "create_time": str(datetime.now()),
            "param_list": param_list
        }
        return resource

    if current_app.config.get("REGISTER_ENABLE", False) and current_app.config.get("REGISTER_SERVER"):
        resource_list = []
        url_rules_dict = {}
        for blueprint_name, blueprint in app.blueprints.items():
            group_key = f'{blueprint_name}|{blueprint.url_prefix}'
            if blueprint.url_prefix not in ["/swagger-ui"]:
                url_rules_dict[group_key] = []
                # 遍历全局 URL 规则
                for rule in app.url_map.iter_rules():
                    # 筛选出属于当前蓝图的规则
                    if rule.endpoint.startswith(f"{blueprint_name}."):
                        url_rules_dict[group_key].append(rule)

        for parent_resource in url_rules_dict:
            symbol = uuid.uuid1().hex
            label, url = parent_resource.split("|")
            resource = package_resource(label=label, symbol=symbol, url=url, access=0, type=0)
            resource["children"] = []

            for child_resource in url_rules_dict[parent_resource]:
                view_func = app.view_functions[child_resource.endpoint]

                method = list(child_resource.methods - {'HEAD', 'OPTIONS'})[0]
                inter_desc, param_desc_dict, return_desc = split_doc(child_resource, app)
                if method == "POST":
                    path = replace_symbol(child_resource.rule)
                    if "{" in path and "}" in path:
                        path_params = extract_path_parameters(child_resource, param_desc_dict)
                        param_list = extract_post_body(view_func,
                                                       not_allow_list=[param["name"] for param in path_params],
                                                       param_desc_dict=param_desc_dict)
                        param_list = param_list + param_list
                    else:
                        param_list = extract_post_body(view_func, param_desc_dict=param_desc_dict)
                elif method == "GET":
                    param_list = extract_path_parameters(child_resource, param_desc_dict) + extract_get_parameters(
                        child_resource, view_func, param_desc_dict)
                else:
                    param_list = []
                resource["children"].append(
                    package_resource(label=view_func._title, symbol=child_resource.rule, access=1, type=2,
                                     method=method,
                                     url=child_resource.rule,
                                     description=inter_desc, param_list=param_list))
            resource_list.append(resource)
        try:
            httpx = import_module("httpx")
        except ImportError as e:
            raise Exception(f"httpx is not exist,run:pip install httpx==0.24.1")
        with httpx.Client(**{"timeout": None}) as session:
            try:
                res = session.request("post", url=current_app.config.get(
                    "REGISTER_SERVER") + "/icp/authResource/resource_register", json={
                    "resource_list": resource_list
                })
                return res
            except Exception as e:
                raise e


# def setup_static(app):
#     @app.route("/static/<filename>")
#     def static_resource(filename, **kwargs):
#         """
#         方法说明
#         :param download_key:
#         :return:
#         """
#         return send_from_directory('static', filename)

def setup_data_download(app):
    @app.route(f"{current_app.config.get('ROUTE_PREFIX')}/download/data_download", methods=['POST'])
    def data_download(download_key, data_len, params=None, column_list=None, page_size=10, file_name=""):
        """
        方法说明
        :param download_key:
        :return:
        """
        if not file_name:
            file_name = "data_export"
        if not data_len:
            data_len = [1, 1000]
        try:
            offset = data_len[0] - 1
            size = data_len[1] - offset
        except:
            raise Exception("请填写正确的导出条数")
        func = download_func_dict.get(download_key, {})
        request_param = {"offset": offset, "size": size}
        signature = inspect.signature(func)
        for parameter_name, parameter in signature.parameters.items():
            if params.get(parameter_name):
                request_param[parameter_name] = params[parameter_name]
        table_body_list = func(**request_param)
        sta_map_dict = format_to_table_download(table_head_list=column_list, table_body_list=table_body_list)
        url, file_key = upload_result_url(sta_map_dict, file_name=file_name)
        return url


def setup_scheduler(app):
    if current_app.config.get("SCHEDULER_ENABLE", False):
        try:
            flask_apscheduler = import_module("flask_apscheduler")
        except ImportError as e:
            raise Exception(f"flask_apscheduler is not exist,run:pip install flask_apscheduler==1.13.1")
        scheduler = flask_apscheduler.APScheduler()
        scheduler.init_app(app)
        scheduler.start()
        task_list = current_app.config.get("SCHEDULER_TASK_LIST", [])
        if task_list:
            for task in task_list:
                if isinstance(task, dict):
                    task_func = task.get("task_func")
                    func_kwargs = task.get("func_kwargs", {}) or dict()
                    task_enable = task.get("enable", False)
                    task_kwargs = task.get("task_kwargs", {}) or dict()
                    if task_enable:
                        scheduler.add_job(func=task_func, kwargs=func_kwargs, **task_kwargs)

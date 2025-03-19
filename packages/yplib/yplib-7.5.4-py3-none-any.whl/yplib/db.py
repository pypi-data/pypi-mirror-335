from yplib.index import *
from yplib.http_util import *
import pymysql
import sqlparse
import threading

# 创建一个线程本地存储对象
thread_local_yp_lib = threading.local()


# 有关数据库操作的类
def get_connect(database=None, user=None, password=None, charset='utf8mb4', port=3306, host=None):
    return pymysql.connect(database=database, user=user, password=password, charset=charset, port=port, host=host)


def get_connect_from_config(db_config='stock_db', database=None, user=None, password=None, charset=None, port=None, host=None):
    config_db = get_config_data(db_config)
    database = database if database is not None else config_db['database']
    user = user if user is not None else config_db['user']
    host = host if host is not None else config_db['host']
    password = password if password is not None else config_db['password']
    port = port if port is not None else config_db['port'] if 'port' in config_db else 3306
    charset = charset if charset is not None else config_db['charset'] if 'charset' in config_db else 'utf8mb4'
    return get_connect(database=database, user=user, password=password, charset=charset, port=port, host=host)


def exec_sql(sql='', db_conn=None, db_config='stock_db', commit=True, is_log=False, database=None, save_to_thread=False):
    """
    执行 sql 语句, 并且提交, 默认值提交的了
    sql             : 需要执行的 sql
    db_conn         : sql 连接
    db_config       : 连接所在的配置文件
    commit          : 是否提交
    is_log          : 是否记录到 log
    database        : 具体的数据库,会覆盖 db_config 中的
    save_to_thread  : 是否将连接信息保存到 thread 中, 这样, 就不用, 每次都建立连接了
    """
    db_cursor = None
    try:
        if db_conn is None:
            if save_to_thread:
                thread_key = db_config + '_' + database if database is not None else db_config
                if not hasattr(thread_local_yp_lib, 'mysql_conn'):
                    thread_local_yp_lib.mysql_conn = {}
                if thread_key not in thread_local_yp_lib.mysql_conn:
                    thread_local_yp_lib.mysql_conn[thread_key] = get_connect_from_config(db_config, database=database)
                db_conn = thread_local_yp_lib.mysql_conn[thread_key]
            else:
                db_conn = get_connect_from_config(db_config, database=database)
        if sql is None or sql == '':
            if is_log:
                to_log_file("db_conn is None or sql is None or sql == '', so return")
            return
        db_cursor = db_conn.cursor()
        if isinstance(sql, list) or isinstance(sql, set):
            for s in sql:
                if is_log:
                    to_log_file(s)
                db_cursor.execute(s)
        else:
            if is_log:
                to_log_file(sql)
            db_cursor.execute(str(sql))
        if commit:
            db_conn.commit()
    finally:
        if not save_to_thread:
            if db_cursor is not None:
                db_cursor.close()
            if db_conn is not None:
                db_conn.close()


def get_doris_conn(db_config='doris'):
    # config_db = get_config_data(db_config)
    # my_uri = config_db['uri']
    # my_db_kwargs = {
    #     adbc_driver_manager.DatabaseOptions.USERNAME.value: config_db['username'],
    #     adbc_driver_manager.DatabaseOptions.PASSWORD.value: config_db['password'],
    # }
    # conn = flight_sql.connect(uri=my_uri, db_kwargs=my_db_kwargs, autocommit=True)
    return get_connect_from_config(db_config)


# 执行 sql 语句, 并且提交, 默认值提交的了
def exec_doris_sql(sql='', db_config='wh_doris', database='mx_risk'):
    exec_sql(sql, db_config=db_config, database=database)
    # conn = get_doris_conn(db_config)
    # cursor = conn.cursor()
    # cursor.execute(sql)
    # cursor.close()
    # conn.close()


def get_data_from_doris(sql='', db_config='doris'):
    if not hasattr(thread_local_yp_lib, 'conn_doris'):
        thread_local_yp_lib.conn_doris = get_doris_conn(db_config)
    conn_doris = thread_local_yp_lib.conn_doris
    cursor = conn_doris.cursor()
    cursor.execute(sql)
    return cursor.fetchall()
    # arrow_data = cursor.fetchallarrow()
    # dataframe = arrow_data.to_pandas()
    # json_data = dataframe.to_json(orient='records', date_format='iso')
    # return json.loads(json_data)


def get_data_line_one_from_doris(sql='', db_config='doris'):
    data_list = get_data_from_doris(sql, db_config=db_config)
    if len(data_list):
        return list(data_list[0])
    return None


# 执行 sql 语句, 不提交
def exec_sql_un_commit(sql='', db_conn=None, database=None):
    exec_sql(sql=sql, db_conn=db_conn, commit=False, database=database)


# 执行 sql 获得 数据
def get_data_from_sql(sql='', db_conn=None, db_config='stock_db', is_log=False, database=None, save_to_thread=False):
    db_cursor = None
    try:
        if db_conn is None:
            if save_to_thread:
                thread_key = db_config + '_' + database if database is not None else db_config
                if not hasattr(thread_local_yp_lib, 'mysql_conn'):
                    thread_local_yp_lib.mysql_conn = {}
                if thread_key not in thread_local_yp_lib.mysql_conn:
                    thread_local_yp_lib.mysql_conn[thread_key] = get_connect_from_config(db_config, database=database)
                db_conn = thread_local_yp_lib.mysql_conn[thread_key]
            else:
                db_conn = get_connect_from_config(db_config, database=database)
        if sql is None or sql == '':
            if is_log:
                to_log_file("db_conn is None or sql is None or sql == '', so return")
            return
        db_cursor = db_conn.cursor()
        if is_log:
            to_log_file(sql)
        db_cursor.execute(str(sql))
        data = db_cursor.fetchall()
    finally:
        if not save_to_thread:
            if db_cursor is not None:
                db_cursor.close()
            if db_conn is not None:
                db_conn.close()
    return data


def extract_all_sql(log_content):
    """
    从字符串中提取所有 SQL 语句，并将 `?` 替换为参数，同时提取日志中的 total 信息。
    参数：
        log_content (str): 包含日志信息的字符串。
    返回：
        list: 包含 SQL 语句和总数的元组列表。
              每个元组的第一个元素是 SQL 语句，第二个元素是 total（如果存在）。
    示例：
           log_content = 如下， 返回 list([sql, total])
11:15:27.259 INFO o.s.c.n.e.c.DiscoveryClientOptionalArgsConfiguration : Eureka HTTP Client uses RestTemplate.
11:15:27.315 WARN o.s.c.l.c.LoadBalancerCacheAutoConfiguration$LoadBalancerCaffeineWarnLogger : Spring Cloud LoadBalancer is currently working with the default cache. While this cache implementation is useful for development and tests, it's recommended to use Caffeine cache in production.You can switch to using Caffeine cache, by adding it and org.springframework.cache.caffeine.CaffeineCacheManager to the classpath.
11:15:27.347 INFO o.s.b.a.e.w.EndpointLinksResolver : Exposing 1 endpoint beneath base path '/actuator'
11:15:27.471 INFO c.u.m.r.f.CheckReportCreatorTests : Started CheckReportCreatorTests in 11.792 seconds (process running for 13.368)
11:15:28.843 DEBUG c.u.m.r.f.m.A.findInfo : ==>  Preparing: select t.order_id, t.report_data as report_data_java, l.report_data from analyze_report_java t left join analyze_report_loan l on t.order_id = l.order_id and t.report_type = l.report_type where t.report_type = ? and t.create_time > ? and t.phase_code = 'LOAN' and l.report_data != t.report_data and t.id > 0 order by t.id desc
11:15:28.987 DEBUG c.u.m.r.f.m.A.findInfo : ==> Parameters: smsNewCommon.all(String), 2025-01-09 15:22:00(String)
11:15:33.884 DEBUG c.u.m.r.f.m.A.findInfo : <==      Total: 0
11:15:33.885 DEBUG c.u.m.r.f.m.A.findInfoCredit : ==>  Preparing: select t.order_id, t.report_data as report_data_java, l.report_data from analyze_report_java t left join analyze_report_credit l on t.order_id = l.order_id and t.report_type = l.report_type where t.report_type = ? and t.create_time > ? and t.phase_code = 'PRELOAN' and l.report_data != t.report_data and t.id > 0 order by t.id desc
11:15:33.886 DEBUG c.u.m.r.f.m.A.findInfoCredit : ==> Parameters: smsNewCommon.all(String), 2025-01-09 15:22:00(String)
11:15:36.782 DEBUG c.u.m.r.f.m.A.findInfoCredit : <==      Total: 0
11:15:37.493 INFO c.z.h.HikariDataSource : HikariPool-1 - Shutdown initiated...
11:15:38.426 INFO c.z.h.HikariDataSource : HikariPool-1 - Shutdown completed.
    """
    if len(log_content.split('\n')) == 2:
        log_content += '\n'
    # 匹配 SQL 语句和参数
    sql_pattern = r"Preparing: (.*?)\n.*?Parameters: (.*?)\n"
    # 匹配 total 记录
    total_pattern = r"Total:\s*(\d+)"
    # 查找所有 SQL 语句和参数
    matches = re.findall(sql_pattern, log_content, re.DOTALL)
    # 查找所有 Total 值
    totals = re.findall(total_pattern, log_content)

    sql_list = []
    total_index = 0  # 记录 total 匹配的位置

    for sql, parameters in matches:
        sql = sql.strip()
        # 解析参数
        params_list = [
            param.split("(")[0].strip() for param in parameters.split(", ")
        ]

        # 依次替换 `?` 为参数值
        for param in params_list:
            sql = sql.replace("?", f"'{param}'", 1)

        # 取对应的 total 值
        total = int(totals[total_index]) if total_index < len(totals) else None
        total_index += 1

        sql_list.append((sql, total))
    return sql_list


def format_sql(sql):
    return sqlparse.format(sql, reindent=True, keyword_case="upper")


def deal_sql(sql):
    sql = sql.replace('\n', ' ')
    sql = re.sub(r'\s+', ' ', sql).strip()
    return sql


def compress_sql(sql):
    return re.sub(r'\s+', ' ', str(sql).replace('\n', ' ').replace('\r', ' ')).strip()






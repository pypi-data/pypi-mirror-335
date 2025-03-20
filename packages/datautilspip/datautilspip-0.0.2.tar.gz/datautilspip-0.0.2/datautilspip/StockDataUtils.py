#%%
# coding: utf-8
from asyncio import sleep
import requests
import os
import polars as pl
from pathlib import Path
import numpy as np
import csv
from datetime import datetime
import pymysql
from sqlalchemy import create_engine



#%%

# 数据导入类
"""
导入股票类数据，全都是classmethod，返回一个json，scheme为： 
{   
    'name':证券名称 str
    'time':时间 datetime
    'dealNum':成交量（手）int
    'dealPrice':成交额 float
    'highPrice'：到目前为止最高价 float
    'lowPrice'：到目前为止最低价 float
    'nowPrice'：当前价格 float
}

"""
# 环境变量数据



# ======== 数据获取工具-通过各种api接口获得免费的数据 ========
class StockDataGetUtils:
    # 数据设置  
    # 构造函数
    def __init__(self):
        pass


    # ======  聚合数据api  ======
    @classmethod
    def juhedata(cls,api_keys_list:list,gid:str=None,stock_type:str=None)->dict:
        """
        说明：
        股票编号，上海股市以sh开头，深圳股市以sz开头如：sh601009（type为0或者1时gid不传）
        type:0代表上证综合指数，1代表深证成份指数(输入此字段时,gid字段不起作用)
        """
        for key in api_keys_list:
            # 基本参数配置
            apiUrl = 'http://web.juhe.cn/finance/stock/hs'  # 接口请求URL
            # 接口请求入参配置
            requestParams = {
                'key': key,
                'gid': gid,
                'type': stock_type,
            }
            # 发起接口网络请求
            response = requests.get(apiUrl, params=requestParams)
            # 解析响应结果
            if response.status_code == 200:
                responseResult = response.json()
                # 网络请求成功。可依据业务逻辑和接口文档说明自行处理。
                result = responseResult['result']
                error_code = responseResult['error_code']

                # 错误码解析
                if error_code == 0 and type(result) == dict:
                    # 判断最大和最小数据是否弄反了（接口的bug）
                    if float(result['highPri']) < float(result['lowpri']):
                        # 反了的话就交换回来
                        result['highPri'],result['lowpri'] = result['lowpri'],result['highPri']
                    result_interpret = {   
                        'name':result['name'],
                        'time':result['time'],
                        'dealNum':int(result['dealNum'])/100, # 返回的单位是手（百股），除以100，变为万股
                        'dealPrice':float(result['dealPri'])/10000, # 单位是元，除以一万变为万元
                        'highPrice':float(result['highPri']),
                        'lowPrice':float(result['lowpri']),
                        'nowPrice':float(result['nowpri']),
                    } 
                    print('请求成功，返回数据')
                    return result_interpret

                else:
                    error_dict = {
                        10001:  '错误的请求KEY',
                        10002:	'该KEY无请求权限',
                        10003:	'KEY过期',	
                        10004:	'错误的OPENID',	
                        10005:	'应用未审核超时，请提交认证',	
                        10007:	'未知的请求源',	
                        10008:	'被禁止的IP',	
                        10009:	'被禁止的KEY',
                        10011:	'当前IP请求超过限制',	
                        10012:	'请求超过次数限制',
                        10013:	'测试KEY超过请求限制',	
                        10014:	'系统内部异常(调用充值类业务时，请务必联系客服或通过订单查询接口检测订单，避免造成损失)',	
                        10020:	'接口维护',	
                        10021:	'接口停用',	
                        202101: '参数错误',
                        202102: '查询不到结果',
                        202103: '网络异常'
                    }
                    print('请求成功，但结果的错误码为：'+error_dict[error_code]+'，更换api尝试')
            else:
                print(response.status_code)
                # 网络异常等因素，解析结果异常。可依据业务逻辑自行处理。
                print('请求异常')
                return
        print('所有api尝试完毕,仍然失败')
        return   
    # 聚合数据api-


#======== 保存数据工具-将数据保存到mysql或其他路径 ========
class DataSaveUtils:
    def __init__(self):
        pass

    
    # 工具：将csv储存为mysql
    def __init__(self):
        pass

    # ====== 将csv添加到数据表 ======
    @classmethod
    def csv_to_mysql(cls, sql_config_dict:dict, csv_file: str):

        """
        将csv数据插入到 MySQL 表中， 
        插入前确保csv列名和表列名一致

        sql_config_dict配置
        :param data_dict: 包含列名和值的字典
        :param table_name: 目标表名
        :param host: MySQL 主机地址
        :param user: MySQL 用户名
        :param password: MySQL 密码
        :param database: 数据库名
        """

        host = sql_config_dict['host']
        user = sql_config_dict['user']
        password = sql_config_dict['password']
        database = sql_config_dict['database']
        table_name = sql_config_dict['table_name']
        charset = sql_config_dict['charset']
        cursorclass = sql_config_dict['cursorclass']
    
        try:
            # 连接到 MySQL 数据库
            connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                charset=charset,
                cursorclass=cursorclass
            )
            print("成功连接到数据库")
        except pymysql.Error as err:
            print(f"连接数据库时出错: {err}")
            return

        try:
            # 打开 CSV 文件
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader)  # 获取 CSV 文件的标题行
                print("成功读取 CSV 文件")

                try:
                    with connection.cursor() as cursor:
                        # 插入数据
                        placeholders = ', '.join(['%s'] * len(headers))
                        insert_query = f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES ({placeholders})"
                        for row in reader:
                            cursor.execute(insert_query, row)
                        connection.commit()
                        print("数据插入成功")
                except pymysql.Error as err:
                    print(f"插入数据时出错: {err}")
        except FileNotFoundError:
            print(f"未找到 CSV 文件: {csv_file}")
        finally:
            # 关闭数据库连接
            connection.close()


    # ====== 将字典数据插入到 MySQL 表中 ======
    @classmethod
    def dict_to_mysql(cls, sql_config_dict: dict, data_dict: dict):
        """
        将字典数据插入到 MySQL 表中，
        插入前确保dict键名和表列名一致

        sql_config_dict配置
        :param data_dict: 包含列名和值的字典
        :param table_name: 目标表名
        :param host: MySQL 主机地址
        :param user: MySQL 用户名
        :param password: MySQL 密码
        :param database: 数据库名
        """
        host = sql_config_dict['host']
        user = sql_config_dict['user']
        password = sql_config_dict['password']
        database = sql_config_dict['database']
        table_name = sql_config_dict['table_name']
        charset = sql_config_dict['charset']
        cursorclass = sql_config_dict['cursorclass']

        try:
            # 连接到 MySQL 数据库
            connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                charset=charset,
                cursorclass=cursorclass
            )

            with connection.cursor() as cursor:
                # 查找 datetime 类型的字段名
                datetime_column = None
                for key, value in data_dict.items():
                    if isinstance(value, (datetime, str)):
                        try:
                            if isinstance(value, str):
                                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                            datetime_column = key
                            break
                        except ValueError:
                            continue

                if datetime_column:
                    # 读取数据库最后一行的 datetime 数据
                    select_query = f"SELECT {datetime_column} FROM {table_name} ORDER BY {datetime_column} DESC LIMIT 1"
                    cursor.execute(select_query)
                    result = cursor.fetchone()
                    if result:
                        last_datetime = result[datetime_column]
                        if isinstance(last_datetime, str):
                            last_datetime = datetime.strptime(last_datetime, '%Y-%m-%d %H:%M:%S')
                        new_datetime = data_dict[datetime_column]
                        if isinstance(new_datetime, str):
                            new_datetime = datetime.strptime(new_datetime, '%Y-%m-%d %H:%M:%S')
                        if new_datetime <= last_datetime:
                            print(f"新数据的时间 {new_datetime} 小于或等于数据库中最后一行数据的时间 {last_datetime}，不保存。")
                            return

                # 构建插入语句
                columns = ', '.join(data_dict.keys())
                placeholders = ', '.join(['%s'] * len(data_dict))
                insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                values = tuple(data_dict.values())

                # 执行插入语句
                cursor.execute(insert_query, values)

            # 提交事务
            connection.commit()
            print(f"成功插入数据到 {table_name} 表")
        except pymysql.Error as err:
            print(f"插入数据时出错: {err}")
        finally:
            # 关闭数据库连接
            if connection:
                connection.close()


#%%
# ======== mysql工具，用于除了保存外的其他mysql操作 ========
class MySQLUtils:
    def __init__(self):
        pass

    # ====== 执行mysql脚本 ======
    @classmethod
    def execute_mysql_script(cls,sql_config_dict:dict, script_path:str):
        """
        执行mysql脚本  
        
        sql_config_dict配置
        :param data_dict: 包含列名和值的字典
        :param table_name: 目标表名
        :param host: MySQL 主机地址
        :param user: MySQL 用户名
        :param password: MySQL 密码
        :param database: 数据库名
        """
        host = sql_config_dict['host']
        user = sql_config_dict['user']
        password = sql_config_dict['password']
        database = sql_config_dict['database']
        table_name = sql_config_dict['table_name']
        charset = sql_config_dict['charset']
        cursorclass = sql_config_dict['cursorclass']
        try:
            # 连接到 MySQL 数据库
            connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                charset=charset,
                cursorclass=cursorclass
            )
            print("成功连接到数据库")

            try:
                with open(script_path, 'r', encoding='utf-8') as file:
                    # 读取 SQL 脚本内容
                    sql_script = file.read()
                    # 按分号分割 SQL 语句
                    sql_commands = sql_script.split(';')

                    with connection.cursor() as cursor:
                        for command in sql_commands:
                            if command.strip():
                                # 执行 SQL 语句
                                cursor.execute(command)
                        # 提交事务
                        connection.commit()
                        print("SQL 脚本执行成功")
            except FileNotFoundError:
                print(f"未找到 SQL 脚本文件: {script_path}")
            except pymysql.Error as err:
                print(f"执行 SQL 脚本时出错: {err}")
        except pymysql.Error as err:
            print(f"连接数据库时出错: {err}")
        finally:
            if connection:
                # 关闭数据库连接
                connection.close()
    
    # ====== 读取mysql数据为polars-df ======
    @classmethod
    def read_mysql(cls,sql_config_dict:dict, sql_query:str)->pl.DataFrame:
        """
        从获取sql_query的请求结果

        sql_config_dict配置
        :param data_dict: 包含列名和值的字典
        :param table_name: 目标表名
        :param host: MySQL 主机地址
        :param user: MySQL 用户名
        :param password: MySQL 密码
        :param database: 数据库名
        """
        host = sql_config_dict['host']
        user = sql_config_dict['user']
        password = sql_config_dict['password']
        database = sql_config_dict['database']
        table_name = sql_config_dict['table_name']
        charset = sql_config_dict['charset']
        cursorclass = sql_config_dict['cursorclass']
        port = '3306'

        # 构建数据库连接字符串
        engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}')

        # 表名
        table_name = 'shanghai_index_daily_data'

        # 构建完整的 SQL 查询语句
        query = f"SELECT * FROM {table_name}"

        # 从数据库中读取数据
        df = pl.read_database(query, engine)

        # 返回df
        return df



    
    
# %%

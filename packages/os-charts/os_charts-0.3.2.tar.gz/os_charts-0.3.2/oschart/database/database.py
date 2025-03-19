#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/3/8 10:50 AM
# @Author  : zy
# @Site    :
# @File    : database.py
# @Software: PyCharm
"""
文件功能:
数据库相关
"""

from dbutils.pooled_db import PooledDB
from elasticsearch import Elasticsearch
from pymysql.cursors import DictCursor
import pymysql.cursors


class SingletonMeta(type):
    """
    元类
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class MysqlDb(metaclass=SingletonMeta):
    """
    mysql 客户端，采用单例模式和连接池管理数据库连接
    """

    def __init__(self, **connection_kwargs):
        super(MysqlDb, self).__init__()
        # 配置连接池
        self.pool = PooledDB(
            creator=pymysql,  # 使用链接数据库的模块
            mincached=2,  # 连接池允许的最小连接数
            maxcached=30,  # 连接池允许的最大连接数
            maxshared=3,
            maxconnections=10,
            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待
            setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
            ping=1,  # 有效性校验
            host=connection_kwargs.get("host", ""),
            port=connection_kwargs.get("port", ""),
            user=connection_kwargs.get("user", ""),
            password=connection_kwargs.get("password", ""),
            database=connection_kwargs.get("database", ""),
            charset=connection_kwargs.get("charset", "utf8mb4"),
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10,  # 设置连接超时
            read_timeout=30,  # 设置读取超时
        )

    def __enter__(self):
        self.conn, self.cs = self.get_conn()
        return self.cs

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 确保游标和连接关闭，防止连接池中的连接泄漏
        try:
            if exc_type is None:
                self.conn.commit()  # 提交事务
        except Exception as e:
            print(f"Error committing transaction: {e}")
        finally:
            # 关闭游标和连接，确保资源回收
            self.cs.close()
            self.conn.close()

    def get_conn(self):
        """从连接池中获取连接"""
        conn = self.pool.connection()
        conn.ping(reconnect=True)  # 确保连接有效
        cs = conn.cursor()
        return conn, cs

    def close_pool(self):
        """关闭连接池，通常在程序结束时调用"""
        self.pool.close()

    def get_one(self, sql: str):
        """
        获取单个
        """
        conn, cs = self.get_conn()
        cs.execute(sql)
        res = cs.fetchone()
        self.close_conn_cs(conn, cs)
        return res

    def get_all(self, sql: str):
        """
        获取单个
        """
        conn, cs = self.get_conn()
        cs.execute(sql)
        res = cs.fetchall()
        self.close_conn_cs(conn, cs)
        return res

    @staticmethod
    def close_conn_cs(conn, cs):
        """
        显示关闭
        """
        cs.close()
        conn.close()


class MysqlDbOld(metaclass=SingletonMeta):
    """
    MySQL 客户端，采用单例模式和连接池管理数据库连接
    """

    def __init__(self, **connection_kwargs):
        super(MysqlDbOld, self).__init__()
        self.pool = PooledDB(
            creator=pymysql,
            mincached=2,
            maxcached=30,
            maxshared=3,
            maxconnections=10,
            blocking=True,
            setsession=[],
            ping=1,  # 1: 检查服务器是否可用
            host=connection_kwargs.get("host", ""),
            port=connection_kwargs.get("port", ""),
            user=connection_kwargs.get("user", ""),
            password=connection_kwargs.get("password", ""),
            database=connection_kwargs.get("database", ""),
            charset=connection_kwargs.get("charset", "utf8mb4"),
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10,
            read_timeout=30,
            autocommit=True,  # 自动提交事务，防止事务未提交导致数据不一致
        )

    def __enter__(self):
        self.conn, self.cs = self.get_conn()
        return self.cs

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()  # 遇到异常时回滚
        except Exception as e:
            print(f"Transaction error: {e}")
        finally:
            self.cs.close()
            self.conn.close()

    def get_conn(self):
        """从连接池中获取连接，确保连接有效"""
        conn = self.pool.connection()
        conn.ping(reconnect=True)  # 确保连接有效
        cs = conn.cursor()
        return conn, cs

    def close_pool(self):
        """关闭连接池"""
        self.pool.close()

    def get_one(self, sql: str, retry_count=3):
        """获取单个记录，最多重试 retry_count 次"""
        conn, cs = self.get_conn()
        try:
            cs.execute(sql)
            res = cs.fetchone()
            if res is None:
                # 如果查询返回空结果，不需要重试
                raise RuntimeError(f"Query returned empty result: {sql}")
            return res
        except (pymysql.OperationalError, pymysql.InterfaceError, RuntimeError) as e:
            if retry_count > 0:
                print(f"MySQL query failed, reconnecting... {e}")
                conn.close()  # 关闭失效连接
                # 递归重试，减小重试次数
                return self.get_one(sql, retry_count - 1)
            else:
                # 超过最大重试次数仍然失败，抛出异常
                raise RuntimeError(f"Query failed after 3 retries: {e}")
        finally:
            self.close_conn_cs(conn, cs)

    def get_all(self, sql: str, retry_count=3):
        """获取所有记录，最多重试 retry_count 次"""
        conn, cs = self.get_conn()
        try:
            cs.execute(sql)
            res = cs.fetchall()
            if not res:
                # 如果查询返回空结果，不需要重试
                raise RuntimeError(f"Query returned empty result: {sql}")
            return res
        except (pymysql.OperationalError, pymysql.InterfaceError, RuntimeError) as e:
            if retry_count > 0:
                print(f"MySQL query failed, reconnecting... {e}")
                conn.close()  # 关闭失效连接
                # 递归重试，减小重试次数
                return self.get_all(sql, retry_count - 1)
            else:
                # 超过最大重试次数仍然失败，抛出异常
                raise RuntimeError(f"Query failed after 3 retries: {e}")
        finally:
            self.close_conn_cs(conn, cs)

    @staticmethod
    def close_conn_cs(conn, cs):
        """关闭游标和连接"""
        cs.close()
        conn.close()


class EsDb(object):
    """
    es 客户端
    """

    def __init__(self, **connection_kwargs):
        super(EsDb, self).__init__()
        # 初始化
        self.client = Elasticsearch(
            hosts=[{"host": connection_kwargs.get("host", ""), "port": connection_kwargs.get("port", "")}],
            http_auth=(connection_kwargs.get("user", ""), connection_kwargs.get("password", "")),
            scheme="http",
            timeout=100,
            max_retries=3,
            retry_on_timeout=True,
        )

    def __enter__(self):
        # 返回游标进行执行操作
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class OsChartsDb(object):
    """
    数据库配置类
    """

    def __init__(self):
        self._db_mysql = None
        self._db_es = None

    def set_mysql_config(self, **kwargs):
        """
        pass
        """
        self._db_mysql = MysqlDb(**kwargs)

    def set_es_config(self, **kwargs):
        """
        pass
        """
        self._db_es = EsDb(**kwargs)

    @property
    def get_db_mysql(self):
        """
        mysql 对象
        """
        return self._db_mysql

    @property
    def get_db_es(self):
        """
        es 对象
        """
        return self._db_es


os_chart_db = OsChartsDb()


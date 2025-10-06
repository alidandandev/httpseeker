#!/usr/bin/env python
# _*_ coding:utf-8 _*_
from __future__ import annotations

import datetime
import decimal

from typing import Any

import pymysql

from dbutils.pooled_db import PooledDB

from httpseeker.common.errors import SQLSyntaxError
from httpseeker.common.log import log
from httpseeker.core.get_conf import httpseeker_config
from httpseeker.enums.query_fetch_type import QueryFetchType
from httpseeker.enums.sql_type import SqlType
from httpseeker.utils.enum_control import get_enum_values
from httpseeker.utils.request.vars_recorder import record_variables


class MysqlDB:
    def __init__(self) -> None:
        self._pool = None
        self._enabled = False
        # 只有配置了有效的 MySQL 连接信息才初始化连接池
        if all([
            httpseeker_config.MYSQL_HOST,
            httpseeker_config.MYSQL_PORT,
            httpseeker_config.MYSQL_USER,
            httpseeker_config.MYSQL_DATABASE,
        ]):
            try:
                self._pool = PooledDB(
                    pymysql,
                    host=httpseeker_config.MYSQL_HOST,
                    port=httpseeker_config.MYSQL_PORT,
                    user=httpseeker_config.MYSQL_USER,
                    password=httpseeker_config.MYSQL_PASSWORD,
                    database=httpseeker_config.MYSQL_DATABASE,
                    charset=httpseeker_config.MYSQL_CHARSET,
                    maxconnections=15,
                    blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待
                    autocommit=False,  # 是否自动提交
                )
                self._enabled = True
            except Exception as e:
                log.warning(f'MySQL 连接初始化失败，MySQL 功能将不可用: {e}')
                self._enabled = False
        else:
            log.info('MySQL 配置未完整提供，跳过 MySQL 连接初始化')

    def init(self) -> tuple[Any, pymysql.cursors.DictCursor]:  # type: ignore
        """
        初始化连接和游标

        :return:
        """
        if not self._enabled or not self._pool:
            raise SQLSyntaxError('MySQL 未启用或连接池未初始化，无法执行 SQL 操作')
        conn = self._pool.connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)  # type: ignore
        return conn, cursor

    @staticmethod
    def close(conn: Any, cursor: pymysql.cursors.DictCursor) -> None:  # type: ignore
        """
        关闭游标和数据库连接

        :return:
        """
        cursor.close()
        conn.close()

    def query(self, sql: str, fetch: QueryFetchType = QueryFetchType.ALL) -> dict | list | None:
        """
        数据库查询

        :param sql:
        :param fetch: 查询条件; one: 查询一条数据; all: 查询所有数据
        :return:
        """
        conn, cursor = self.init()
        data = {}
        try:
            cursor.execute(sql)
            if fetch == QueryFetchType.ONE:
                query_data = cursor.fetchone()
            elif fetch == QueryFetchType.ALL:
                query_data = cursor.fetchall()
            else:
                raise SQLSyntaxError(f'查询条件 {fetch} 错误, 请使用 one / all')
        except Exception as e:
            log.error(f'执行 SQL 失败: {e}')
            raise e
        else:
            log.info(f'执行 SQL 成功: {query_data}')
            if not query_data:
                return None
            try:

                def format_row(row: dict) -> None:
                    for k, v in row.items():
                        if isinstance(v, decimal.Decimal):
                            if v % 1 == 0:
                                data[k] = int(v)
                            data[k] = float(v)
                        elif isinstance(v, datetime.datetime):
                            data[k] = str(v)
                        else:
                            data[k] = v

                if isinstance(query_data, dict):
                    format_row(query_data)
                    return data
                if isinstance(query_data, list):
                    data_list = []
                    for i in query_data:
                        format_row(i)
                        data_list.append(i)
                    return data_list
            except Exception as e:
                log.error(f'序列化 SQL 查询结果失败: {e}')
                raise e
        finally:
            self.close(conn, cursor)

    def execute(self, sql: str) -> int:
        """
        执行 sql 操作

        :return:
        """
        conn, cursor = self.init()
        try:
            rowcount = cursor.execute(sql)
            conn.commit()
        except Exception as e:
            conn.rollback()
            log.error(f'执行 SQL 失败: {e}')
            raise e
        else:
            log.info('执行 SQL 成功')
            return rowcount
        finally:
            self.close(conn, cursor)

    def exec_case_sql(self, sql: str, fetch: QueryFetchType | None, env: str | None = None) -> dict | list | int | None:
        """
        执行用例 sql

        :param sql:
        :param fetch:
        :param env:
        :return:
        """
        # 获取返回数据
        if isinstance(sql, str):
            log.info(f'执行 SQL: {sql}')
            if sql.startswith(SqlType.select):
                if fetch is None:
                    fetch = QueryFetchType.ALL
                return self.query(sql, fetch)
            else:
                return self.execute(sql)

        # 设置变量
        if isinstance(sql, dict):
            log.info(f'执行变量提取 SQL: {sql["sql"]}')
            key = sql['key']
            set_type = sql['type']
            sql_text = sql['sql']
            json_path = sql['jsonpath']
            query_data = self.query(sql_text)
            if not query_data:
                raise SQLSyntaxError('变量提取失败，SQL 查询结果为空')
            record_variables(json_path, query_data, key, set_type, env)  # type: ignore

    def sql_verify(self, sql: str) -> None:
        if not self._enabled:
            raise SQLSyntaxError('MySQL 未启用，无法执行 SQL 验证')
        sql_types = get_enum_values(SqlType)
        if not any(sql.startswith(_) for _ in sql_types):
            raise SQLSyntaxError(f'SQL 中存在非法命令类型, 仅支持: {sql_types}')

    @property
    def is_enabled(self) -> bool:
        """检查 MySQL 是否已启用"""
        return self._enabled


mysql_client = MysqlDB()

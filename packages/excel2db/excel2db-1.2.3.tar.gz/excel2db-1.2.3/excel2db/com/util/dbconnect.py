# -*- coding: utf-8 -*-
"""
数据库连接
在实例化类后，使用时应判断STATUS参数，若参数为0表示连接成功，可以调用
可以使用close方法关闭，也可以等待程序结束后自动关闭
"""
import threading, re

###sqlite
class sqliteCon:
    def __init__(self, dbname):
        """
        :param dbname: 数据库文件路径
        """
        import sqlite3
        self.odbc = sqlite3
        self.dbname = dbname
        self.STATUS = 1  ##判断连接状态，若为1，则未连接，否则已连接

        ###连接数据库
        try:
            self.connect = self.odbc.connect(dbname)
        except Exception:
            self.STATUS = 1
        else:
            self.STATUS = 0

        if not self.STATUS:
            self.cursor = self.connect.cursor()
            self.lock = threading.Lock()

    def close(self):
        if not self.STATUS:
            self.cursor.close()
            self.connect.close()
            self.STATUS = 1

    def acquire(self):
        if not self.STATUS:
            self.lock.acquire()

    def release(self):
        if not self.STATUS:
            self.lock.release()

    def __del__(self):
        if not self.STATUS:
            self.cursor.close()
            self.connect.close()

    def getname(self):
        return self.dbname

    def escape_string(self, st: str):
        return st.replace("'", "''")

class SqlData:
    def __init__(self, dataByRow, dataByCol, columns):
        self.columns = columns
        self.dataByRow = dataByRow
        self.dataByCol = dataByCol

def selectData(conn, sql: str, replace: dict = {}):
    """
    输入sql，输出获得的数据
    :param conn: 数据库链接
    :param sql:
    :param dict: 替换字段名，注意替换的最终结果不能重复，否则替换不会生效
    :return:
    """
    columns = []
    dataByRow = []

    class RowData:
        def toDic(self):
            dic = {}
            for column in columns:
                if hasattr(self, column):
                    dic[column] = getattr(self, column)
            return dic

        def toLis(self):
            lis = []
            for column in columns:
                if hasattr(self, column):
                    lis.append(getattr(self, column))
            return lis

    class ColData:
        def toDic(self):
            dic = {}
            for column in columns:
                if hasattr(self, column):
                    dic[column] = getattr(self, column)
            return dic

        def toLis(self):
            lis = []
            for column in columns:
                if hasattr(self, column):
                    lis.append(getattr(self, column))
            return lis

    dataByCol = ColData()

    conn.cursor.execute(sql)

    ##获取字段名
    for description in conn.cursor.description:
        columns.append(description[0])

    ##替换字段名
    for preColumn in replace:
        if preColumn in columns and replace[preColumn] not in columns:
            columns[columns.index(preColumn)] = replace[preColumn]

    # ##校验字段名
    # for column in columns:
    #     if not re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", column):
    #         raise Exception("sql字段名不符合规则")

    ##生成by字段数据
    for column in columns:
        setattr(dataByCol, column, [])

    ##导入数据
    for row in conn.cursor.fetchall():
        rowData = RowData()
        for index, value in enumerate(row):
            setattr(rowData, columns[index], value)
            getattr(dataByCol, columns[index]).append(value)
        dataByRow.append(rowData)

    sqlData = SqlData(dataByRow, dataByCol, columns)

    return sqlData
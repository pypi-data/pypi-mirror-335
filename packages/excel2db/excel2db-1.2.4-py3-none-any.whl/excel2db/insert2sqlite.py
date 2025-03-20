#!/usr/bin/python

import sys, numpy
from .com.util import dbconnect, fileTool
from . import defaultConf

class insert2sqlite:
    def __init__(self, value):
        """
        插入数据库操作
        :param value: 变量文件
        """
        self.value = value
        self.fileTool = fileTool.fileTool()

        ##数据库文件路径
        if self.value.excelConf["datLoad"] == "":
            self.value.excelConf["datLoad"] = f"./{self.value.excelFileName}.db"
        self.value.datLoad = self.value.excelConf["datLoad"]

        ##连接数据文件，若不存在则创建
        try:
            if self.fileTool.fileIsExists(self.value.datLoad):
                self.fileTool.deleteFile(self.value.datLoad)
            elif self.fileTool.dirIsExists(self.value.datLoad):
                if self.value.datLoad[-1] in ("\\", "/"):
                    self.value.datLoad = self.value.datLoad + self.value.excelFileName + ".db"
                else:
                    item = "\\" if sys.platform == "win32" else "/"
                    self.value.datLoad = self.value.datLoad + item + self.value.excelFileName + ".db"
            self.db = dbconnect.sqliteCon(self.value.datLoad)
            if self.db.STATUS:
                raise Exception("本地数据库连接失败")
            self.value.dbConnect = self.db
        except Exception as e:
            raise Exception("本地数据库创建失败")

    def insert2sqlite(self):
        self.value.tableName = self.value.sheetConf["tableName"] if self.value.sheetConf["tableName"]!='' else self.value.sheetConf["sheetName"]  ##获取主表名
        self.value.tableDtlName = self.value.sheetConf["tableDtlName"] if self.value.sheetConf["tableDtlName"]!='' else self.value.tableName+"_dt"  ##获取明细表名
        creatTableSql = f'CREATE TABLE "main"."{self.db.escape_string(self.value.tableName)}" ("{self.value.sheetConf["mainPrimaryKey"]}" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT%s);'
        creatDtlTableSql = f'CREATE TABLE "main"."{self.db.escape_string(self.value.tableDtlName)}" ("{self.value.sheetConf["detailPrimaryKey"]}" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"{self.value.sheetConf["detailForeignKey"]}" INTEGER NOT NULL%s);'

        ##创建主表
        mainColumn = "" ##创建表语句
        mainColumnIns = "" ##插入表语句
        for column in self.value.columnsType:
            column = self.db.escape_string(column)
            mainColumnIns = mainColumnIns + '"' + column + '"' + ","
            if self.value.columnsType[column] == "int":
                mainColumn += f', "{column}" INTEGER'
            elif self.value.columnsType[column] == "float":
                mainColumn += f', "{column}" REAL'
            elif self.value.columnsType[column] in ("str","date"):
                mainColumn += f', "{column}" TEXT'
            else:
                mainColumn += f', "{column}" BLOB'

        creatTableSql = creatTableSql%mainColumn

        self.db.cursor.execute(creatTableSql)
        self.db.connect.commit()

        if len(self.value.columnsType)==0: ##若标题列无数据，则不添加数据
            return

        if mainColumnIns: mainColumnIns = mainColumnIns[:-1].replace('%','%%')
        ##获取主表名称
        insertMainSql = f"INSERT INTO 'main'.'{self.db.escape_string(self.value.tableName)}'({mainColumnIns}) VALUES (%s);\n"

        ##插入主表
        for data in self.value.mainDBData:
            sqlIn = ""
            for i in data:
                if i != i:
                    sqlIn = sqlIn + "null" + ","
                elif isinstance(i, int) or isinstance(i, float) or isinstance(i, numpy.int64) or isinstance(i, numpy.float64): ##若为数字
                    sqlIn = sqlIn + str(i) + ","
                else:
                    i = self.db.escape_string(i) if isinstance(i, str) else self.db.escape_string(str(i))
                    sqlIn = sqlIn + "'" + i + "',"
            if sqlIn: sqlIn = sqlIn[:-1]
            sql = insertMainSql%sqlIn
            self.db.cursor.execute(sql)

        self.db.connect.commit()

        if self.value.sheetConf["isIncludeDetail"]:
            ##创建明细表
            detailColumn = ""  ##创建表语句
            detailColumnIns = ""  ##插入表语句
            for column in self.value.columnsDtlType:
                column = self.db.escape_string(column)
                detailColumnIns = detailColumnIns + '"' + column + '"' + ","
                detailColumn += f', "{column}" TEXT'

            detailColumnIns = detailColumnIns + '"' + "value" + '"' + ","
            detailColumn += ', "value" TEXT'

            creatDtlTableSql = creatDtlTableSql % detailColumn

            self.db.cursor.execute(creatDtlTableSql)
            self.db.connect.commit()

            if detailColumnIns: detailColumnIns = detailColumnIns[:-1]
            insertDtlSql = f"INSERT INTO 'main'.'{self.db.escape_string(self.value.tableDtlName)}'({self.value.sheetConf['detailForeignKey']},{detailColumnIns}) VALUES (%s);\n"

            ##插入明细表
            for data in self.value.detailDBData:
                sqlIn = ""
                for i in data:
                    if i != i:
                        sqlIn = sqlIn + "null" + ","
                    elif isinstance(i, int) or isinstance(i, float):  ##若为数字
                        sqlIn = sqlIn + self.db.escape_string(str(i)) + ","
                    else:
                        sqlIn = sqlIn + "'" + self.db.escape_string(i) + "',"
                if sqlIn: sqlIn = sqlIn[:-1]
                sql = insertDtlSql % sqlIn
                self.db.cursor.execute(sql)

            self.db.connect.commit()
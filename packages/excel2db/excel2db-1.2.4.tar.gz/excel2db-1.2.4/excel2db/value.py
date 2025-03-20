# -*- coding:utf8 -*-
"""
变量存放
"""
# import xmltodict, zipfile, shutil, os
import inspect

class value:
    def __init__(self):
        ##excel文件相关
        self.excelUrl = "" ##excel文件原始路径
        self.excelSuffix = "" ##excel文件后缀
        self.excelFileName = "" ##excel文件名
        self.sheetList = [] ##sheet工作表列表

        self.excelData = {} ##excel表的所有数据
        self.sheetData = None ##当前sheet表的所有数据
        self.mainTitleData = None  ##当前mainTitle的所有数据
        self.mainData = None  ##当前mainData的所有数据
        self.detailTitleData = None  ##当前mainTitle的所有数据
        self.detailData = None  ##当前mainData的所有数据
        self.scaleData = None  ##当前mainData的所有数据

        self.sheetPosition = [-1, -1, -1, -1]  ##四边定位,分别为（上行，下行，左列，右列）
        self.mainPosition = [-1, -1, -1, -1]
        self.detailPosition = [-1, -1, -1, -1]
        self.mainTitlePosition = [-1, -1, -1, -1]
        self.detailTitlePosition = [-1, -1, -1, -1]
        self.mainDataPosition = [-1, -1, -1, -1]
        self.detailDataPosition = [-1, -1, -1, -1]
        self.scalePosition = [-1, -1, -1, -1]

        self.columnIndex = []  ##选取的列编号
        self.rowIndex = []  ##选取的行编号
        self.mainColumnIndex = [] ##选取的主表列编号
        self.detailColumnIndex = []  ##选取的明细表列编号
        self.titleRowIndex = [] ##选取的标题行编号
        self.dataRowIndex = [] ##选取的数据行编号

        self.cycleColumns = 0 ##明细表一个循环的列数

        ##数据库相关
        self.dbClass = None ##数据库操作类
        self.dbConnect = None ##数据库连接
        self.datLoad = ""  ##生成的数据库文件路径
        self.datLoad = "./test.db"
        self.tableName = "" ##当前主表名
        self.tableDtlName = ""##明细表名
        self.columnsType = {} ##主表字段名及类型
        self.columnsDtlType = []##明细表字段名
        self.mainDBData = [] ##主表数据
        self.detailDBTitleData = {} ##明细表标题行数据
        self.detailDBData = [] ##明细表数据

        ##配置文件相关
        self.rawConf = {}  ##合并后的原始配置文件
        self.excelConf = {}  ##当前的excel级别配置文件
        self.excelConfDown = {}  ##当前的excel级别向下配置文件
        self.sheetConf = {}  ##当前的sheet级别配置文件
        self.sheetConfDown = {}  ##当前的sheet级别向下配置文件
        self.mainTitleConf = {}  ##当前的sheet级别配置文件
        self.mainTitleConfDown = {}  ##当前的sheet级别向下配置文件
        self.mainDataConf = {}  ##当前的sheet级别配置文件
        self.mainDataConfDown = {}  ##当前的sheet级别向下配置文件
        self.detailTitleConf = {}  ##当前的sheet级别配置文件
        self.detailTitleConfDown = {}  ##当前的sheet级别向下配置文件
        self.detailDataConf = {}  ##当前的sheet级别配置文件
        self.detailDataConfDown = {}  ##当前的sheet级别向下配置文件
        self.scaleConf = {}  ##当前的scale级别配置文件

        ##错误信息
        self.ERRINFO = ""

        ##日期格式化
        self.dateFormatFunc = {} ##自定义的日期格式化方法

    # def getAllSheetNames(self, file_path):
    #     sheets = []
    #     file_name = os.path.splitext(os.path.split(file_path)[-1])[0]
    #     # Make a temporary directory with the file name
    #     directory_to_extract_to = os.path.join(file_name)
    #     os.mkdir(directory_to_extract_to)
    #     # Extract the xlsx file as it is just a zip file
    #     zip_ref = zipfile.ZipFile(file_path, 'r')
    #     zip_ref.extractall(directory_to_extract_to)
    #     zip_ref.close()
    #     # Open the workbook.xml which is very light and only has meta data, get sheets from it
    #     path_to_workbook = os.path.join(directory_to_extract_to, 'xl', 'workbook.xml')
    #     with open(path_to_workbook, 'rb') as f:
    #         xml = f.read()
    #         dictionary = xmltodict.parse(xml)
    #         for sheet in dictionary['workbook']['sheets']['sheet']:
    #             if '@state' in sheet.keys():  # 判断表是否可见，如果不可见，有state属性为hidden
    #                 pass
    #             else:
    #                 sheet_details = sheet['@name']
    #                 sheets.append(sheet_details)
    #     # Delete the extracted files directory
    #     shutil.rmtree(directory_to_extract_to)
    #     return sheets

    def robackSheetConf(self):
        self.sheetData = None  ##当前sheet表的所有数据
        self.mainTitleData = None  ##当前mainTitle的所有数据
        self.mainData = None  ##当前mainData的所有数据
        self.detailTitleData = None  ##当前mainTitle的所有数据
        self.detailData = None  ##当前mainData的所有数据
        self.scaleData = None  ##当前mainData的所有数据

        self.sheetPosition = [-1, -1, -1, -1]  ##四边定位,分别为（上行，下行，左列，右列）
        self.mainPosition = [-1, -1, -1, -1]
        self.detailPosition = [-1, -1, -1, -1]
        self.mainTitlePosition = [-1, -1, -1, -1]
        self.detailTitlePosition = [-1, -1, -1, -1]
        self.mainDataPosition = [-1, -1, -1, -1]
        self.detailDataPosition = [-1, -1, -1, -1]
        self.scalePosition = [-1, -1, -1, -1]

        self.columnIndex = []  ##选取的列编号
        self.rowIndex = []  ##选取的行编号
        self.mainColumnIndex = []  ##选取的主表列编号
        self.detailColumnIndex = []  ##选取的明细表列编号
        self.titleRowIndex = []  ##选取的标题行编号
        self.dataRowIndex = []  ##选取的数据行编号
        self.cycleColumns = 0  ##明细表一个循环的列数

        ##数据库相关
        self.tableName = ""  ##当前主表名
        self.tableDtlName = ""  ##明细表名
        self.columnsType = {}  ##主表字段名及类型
        self.columnsDtlType = []  ##明细表字段名
        self.mainDBData = []  ##主表数据
        self.detailDBTitleData = {}  ##明细表标题行数据
        self.detailDBData = []  ##明细表数据

        ##配置文件相关
        self.mainTitleConf = {}  ##当前的sheet级别配置文件
        self.mainTitleConfDown = {}  ##当前的sheet级别向下配置文件
        self.mainDataConf = {}  ##当前的sheet级别配置文件
        self.mainDataConfDown = {}  ##当前的sheet级别向下配置文件
        self.detailTitleConf = {}  ##当前的sheet级别配置文件
        self.detailTitleConfDown = {}  ##当前的sheet级别向下配置文件
        self.detailDataConf = {}  ##当前的sheet级别配置文件
        self.detailDataConfDown = {}  ##当前的sheet级别向下配置文件
        self.scaleConf = {}  ##当前的scale级别配置文件

        ##错误信息
        self.ERRINFO = ""
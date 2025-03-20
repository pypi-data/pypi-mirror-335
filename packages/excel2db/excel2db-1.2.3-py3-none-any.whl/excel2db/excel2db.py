# -*- coding:utf8 -*-
"""
用于excel转sqlite数据库
注意：
依据变量修改配置文件，应在cheakConf中进行
依据配置文件修改变量，应在配置文件完全生成后进行
"""
from . import value, cheakConf, excel

class excel2db:

    def __init__(self, *configFileUrl):
        """
        :param *configFileUrl: 支持直接传入python字典或者配置json或者配置文件路径
        """
        self.value = value.value() ##生成变量文件
        self.value.rawConf = cheakConf.combinExcelConf(*configFileUrl) ##生成配置文件

    def excel2db(self, excelUrl):
        ##执行excel级别转换
        excelManager = excel.excel(self.value, self.value.rawConf)
        excelManager.excel(excelUrl)

    def setDateFormatFunc(self, *dateFormat):
        """
        设置日期格式化方法
        """
        for func in dateFormat:
            self.value.dateFormatFunc[func.__name__] = func

    def getDBConnect(self):
        """
        获取数据库链接
        """
        return self.value.dbConnect

    def getMainColumn(self):
        """
        获取标题字段
        """
        return self.value.columnsType

    def getMainData(self):
        """
        获取主表数据
        """
        return self.value.mainDBData

    def getDetailColumn(self):
        """
        获取明细字段
        """
        return self.value.columnsDtlType

    def getDetailData(self):
        """
        获取明细数据
        """
        return self.value.detailDBData
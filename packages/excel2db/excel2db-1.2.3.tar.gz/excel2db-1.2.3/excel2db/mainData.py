# -*- coding:utf8 -*-
"""
##执行mainData级别转换
"""
from . import cheakConf, scale
from .com.util.coordinate import coordinate

class mainData:
    def __init__(self, value, conf):

        """
        mainData级别操作
        :param value: 变量文件
        :param conf: mainData级别配置（清洗前）
        """
        self.value = value
        cheakConf.mainDataConf(self.value, conf) ##获取mainData级别配置(清洗后)

    def getRows(self):
        """
        获取当前需要的数据行编号
        :return:
        """
        if "mainDataRows" not in self.value.mainDataConf:
            return

        for rowStr in self.value.mainDataConf["mainDataRows"]:
            tempRows = []
            for rowIn in self.value.dataRowIndex:
                row = rowIn - self.value.mainDataPosition[0] + 2
                if eval(rowStr):
                    tempRows.append(rowIn)

            self.value.dataRowIndex = tempRows

    def mainData(self):
        ##初始化mainData坐标集
        mainDataCoord = coordinate(self.value.mainDataPosition)
        ##获取当前需要的数据行编号
        self.getRows()
        ##清空主表数据集
        self.value.mainDBData = []
        ##判断主表数据集是否存在
        if mainDataCoord.STATUS:  ##若不存在
            return None

        ##若主表数据集存在
        ##调整scale级别
        if "scaleList" in self.value.mainDataConfDown:
            scaleConfList = cheakConf.combinScaleConf(self.value, self.value.mainDataConfDown["scaleList"], self.value.mainDataConfDown, self.value.mainDataPosition, mainDataCoord)  ##scale级别配置文件合并
            for scaleConf in scaleConfList:
                scaleManager = scale.scale(self.value, scaleConf)
                scaleManager.scale()

        ##获取mainData级别数据
        self.value.mainData = self.value.sheetData.iloc[
                                   mainDataCoord.start[0] - 1: mainDataCoord.start[0] + mainDataCoord.rows - 1,
                                   mainDataCoord.start[1] - 1: mainDataCoord.start[1] + mainDataCoord.columns - 1
                                   ]

        ##根据columnsType生成数据
        rows, columns = self.value.mainData.shape  ##行列

        ##统一字段类型
        for i in range(columns):

            ##获取字段类型
            typ = None
            for column in self.value.columnsType:
                if self.value.columnsType[column][1] == i:
                    typ = self.value.columnsType[column][0]
                    break

            if typ == "str":
                pass

        ##获取指定数据


        ##录入数据
        self.value.mainDBData = []
        for i in self.value.dataRowIndex:
            rowData = []
            for j in self.value.mainColumnIndex:
                rowData.append(self.value.sheetData.loc[i,j])
            self.value.mainDBData.append(rowData)


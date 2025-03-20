# -*- coding:utf8 -*-
"""
##执行detailTitle级别转换
"""
from . import cheakConf, scale
from .com.util.coordinate import coordinate
from .com.util import excelTool

class detailTitle:
    def __init__(self, value, conf):

        """
        detailTitle级别操作
        :param value: 变量文件
        :param conf: detailTitle级别配置（清洗前）
        """
        self.value = value
        cheakConf.detailTitleConf(self.value, conf) ##获取detailTitle级别配置(清洗后)

    def detailTitle(self):
        ##初始化detailTitle坐标集
        detailTitleCoord = coordinate(self.value.detailTitlePosition)
        ##清空明细表标题
        self.columnsDtlType = {}
        ##判断明细表标题是否存在
        if detailTitleCoord.STATUS:  ##若不存在
            return 0

        ##若明细表标题存在


        ##调整scale级别
        if "scaleList" in self.value.detailTitleConfDown:
            scaleConfList = cheakConf.combinScaleConf(self.value, self.value.detailTitleConfDown["scaleList"],
                                                      self.value.detailTitleConfDown, self.value.detailTitlePosition,
                                                      detailTitleCoord)  ##scale级别配置文件合并
            for scaleConf in scaleConfList:
                scaleManager = scale.scale(self.value, scaleConf)
                scaleManager.scale()

        ##获取detailTitle级别数据
        self.value.detailTitleData = self.value.sheetData.iloc[
                              detailTitleCoord.start[0] - 1: detailTitleCoord.start[0] + detailTitleCoord.rows - 1,
                              detailTitleCoord.start[1] - 1: detailTitleCoord.start[1] + detailTitleCoord.columns - 1
                              ]

        ##根据columnsType生成数据
        rows, columns = self.value.detailTitleData.shape  ##行列
        if len(self.value.detailTitleConf["detailTitleName"]) != rows:
            raise Exception("明细表标题行与配置文件数量不符")
        else:
            self.value.columnsDtlType = self.value.detailTitleConf["detailTitleName"].copy()

        ##录入数据
        self.value.detailDBTitleData = {} ##清空明细表标题行数据
        for i in range(detailTitleCoord.start[1] - 1, detailTitleCoord.start[1] + detailTitleCoord.columns - 1):
            value = []
            for j in self.value.titleRowIndex:
                a = self.value.sheetData.iloc[j, i]
                value.append(excelTool.toStr(a))
            self.value.detailDBTitleData[i] = value
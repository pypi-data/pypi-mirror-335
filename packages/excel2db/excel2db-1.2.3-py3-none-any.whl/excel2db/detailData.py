# -*- coding:utf8 -*-
"""
##执行detailData级别转换
"""
from . import cheakConf, scale
from .com.util.coordinate import coordinate
from .com.util import excelTool

class detailData:
    def __init__(self, value, conf):

        """
        detailData级别操作
        :param value: 变量文件
        :param conf: detailData级别配置（清洗前）
        """
        self.value = value
        cheakConf.detailDataConf(self.value, conf) ##获取detailData级别配置(清洗后)

    def detailData(self):
        ##初始化detailData坐标集
        detailDataCoord = coordinate(self.value.detailDataPosition)
        ##清空明细表标题
        self.columnsDtlType = {}
        ##判断明细表标题是否存在
        if detailDataCoord.STATUS:  ##若不存在
            return 0

        ##若明细表标题存在
        ##调整scale级别
        if "scaleList" in self.value.detailDataConfDown:
            scaleConfList = cheakConf.combinScaleConf(self.value, self.value.detailDataConfDown["scaleList"],
                                                      self.value.detailDataConfDown, self.value.detailDataPosition,
                                                      detailDataCoord)  ##scale级别配置文件合并
            for scaleConf in scaleConfList:
                scaleManager = scale.scale(self.value, scaleConf)
                scaleManager.scale()

        ##获取detailData级别数据
        self.value.detailDataData = self.value.sheetData.iloc[
                                     detailDataCoord.start[0] - 1: detailDataCoord.start[0] + detailDataCoord.rows - 1,
                                     detailDataCoord.start[1] - 1: detailDataCoord.start[1] + detailDataCoord.columns - 1
                                     ]

        ##根据columnsType生成数据
        rows, columns = self.value.detailDataData.shape  ##行列

        ##录入数据
        self.value.detailDBData = []  ##清空明细表数据
        for i in range(detailDataCoord.start[1] - 1, detailDataCoord.start[1] + detailDataCoord.columns - 1):
            for index, j in enumerate(self.value.dataRowIndex):
                value = self.value.detailDBTitleData[i].copy()
                # value.insert(0, j - detailDataCoord.start[0] + 2) ##插入mainid
                value.insert(0, index + 1)  ##插入mainid
                a = self.value.sheetData.iloc[j, i] ##插入数据
                if a != a:
                    continue
                value.append(excelTool.toStr(a))
                self.value.detailDBData.append(value)
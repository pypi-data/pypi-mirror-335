# -*- coding:utf8 -*-
"""
##执行sheet级别转换
"""
from . import cheakConf, mainTitle, mainData, detailTitle, detailData
from .com.util import excelTool

class sheet:
    def __init__(self, value, conf):

        """
        sheet级别操作
        :param value: 变量文件
        :param conf: sheet级别配置（清洗前）
        """
        self.value = value
        cheakConf.sheetConf(self.value, conf) ##获取sheet级别配置(清洗后)

    def sheet(self):
        self.value.robackSheetConf() ##重置sheet配置
        self.value.sheetData = self.value.excelData[self.value.sheetConf["sheetName"]].copy()  ##获取当前sheet数据

        ##定位sheet表
        trueShape = self.value.sheetData.shape ##获取当前sheet表的行列数
        self.value.sheetPosition[0], self.value.sheetPosition[2] = excelTool.letterToNumber(self.value.sheetConf["position"]) ##获取上行和左列
        ##获取下行
        if self.value.sheetConf["rows"] > 0:
            self.value.sheetPosition[1] = self.value.sheetConf["rows"]
        elif self.value.sheetConf["rows"] < 0:
            self.value.sheetPosition[1] = trueShape[0] + self.value.sheetConf["rows"]
        else:
            self.value.sheetPosition[1] = trueShape[0]

        ##获取右列
        if self.value.sheetConf["columns"] > 0:
            self.value.sheetPosition[3] = self.value.sheetConf["columns"]
        elif self.value.sheetConf["columns"] < 0:
            self.value.sheetPosition[3] = trueShape[1] + self.value.sheetConf["columns"]
        else:
            self.value.sheetPosition[3] = trueShape[1]

        ##定位main表和detail表
        if self.value.sheetConf["isIncludeDetail"]: ##若有明细表
            if self.value.sheetConf["detailSplitByColumnID"] != "": ##获取当前分割线
                splitLine = excelTool.letterToNumber(self.value.sheetConf["detailSplitByColumnID"])
            else:
                pass

            self.value.mainPosition = self.value.sheetPosition.copy()
            self.value.mainPosition[3] = splitLine-1

            self.value.detailPosition = self.value.sheetPosition.copy()
            self.value.detailPosition[2] = splitLine

        else:
            self.value.mainPosition = self.value.sheetPosition.copy()

        ##定位mainTitle和mainData
        self.value.mainTitlePosition = self.value.mainPosition.copy()
        self.value.mainTitlePosition[1] = self.value.mainTitlePosition[0] + self.value.sheetConf["titleLines"] - 1
        self.value.mainDataPosition = self.value.mainPosition.copy()
        self.value.mainDataPosition[0] = self.value.mainTitlePosition[0] + self.value.sheetConf["titleLines"]

        ##定位detailTitle和detailData
        if self.value.sheetConf["isIncludeDetail"]: ##若有明细表
            self.value.detailTitlePosition = self.value.detailPosition.copy()
            self.value.detailTitlePosition[1] = self.value.detailTitlePosition[0] + self.value.sheetConf["titleLines"] - 1
            self.value.detailDataPosition = self.value.detailPosition.copy()
            self.value.detailDataPosition[0] = self.value.detailTitlePosition[0] + self.value.sheetConf["titleLines"]

        ##生成选取的行号和列号
        self.value.mainColumnIndex = [i for i in range(self.value.mainTitlePosition[2]-1, self.value.mainTitlePosition[3])]  ##选取的主表列编号
        self.value.detailColumnIndex = [i for i in range(self.value.detailTitlePosition[2]-1, self.value.detailTitlePosition[3])]  ##选取的明细表列编号
        self.value.titleRowIndex = [i for i in range(self.value.mainTitlePosition[0]-1, self.value.mainTitlePosition[1])]  ##选取的标题行编号
        self.value.dataRowIndex = [i for i in range(self.value.mainDataPosition[0]-1, self.value.mainDataPosition[1])]  ##选取的数据行编号

        ##mainTitle级别配置文件
        mainTitleConf = cheakConf.combinMainTitleConf(self.value)  ##mainTitle级别配置文件合并
        mainTitleManager = mainTitle.mainTitle(self.value, mainTitleConf)
        mainTitleManager.mainTitle()

        ##mainData级别配置文件
        mainDataConf = cheakConf.combinMainDataConf(self.value)  ##mainData级别配置文件合并
        mainDataManager = mainData.mainData(self.value, mainDataConf)
        mainDataManager.mainData()

        if self.value.sheetConf["isIncludeDetail"]: ##若有明细表
            ##detailTitle级别配置文件
            detailTitleConf = cheakConf.combindetailTitleConf(self.value)  ##detailTitle级别配置文件合并
            detailTitleManager = detailTitle.detailTitle(self.value, detailTitleConf)
            flag = detailTitleManager.detailTitle()

            if flag != 0: ##若明细表标题行存在
                ##detailData级别配置文件
                detailDataConf = cheakConf.combindetailDataConf(self.value)  ##detailData级别配置文件合并
                detailDataManager = detailData.detailData(self.value, detailDataConf)
                detailDataManager.detailData()

        ##插入数据库
        if self.value.excelConf["isSaveDatabase"] == True:
            self.value.dbClass.insert2sqlite()
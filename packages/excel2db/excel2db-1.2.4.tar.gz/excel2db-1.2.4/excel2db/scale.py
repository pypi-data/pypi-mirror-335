# -*- coding:utf8 -*-
"""
##执行scale级别转换
"""
import traceback

from . import cheakConf
from .com.util import timeTool
import numpy as np

class scale:
    def __init__(self, value, conf):

        """
        scale级别操作
        :param value: 变量文件
        :param conf: scale级别配置（清洗前）
        """
        self.value = value
        cheakConf.scaleConf(self.value, conf) ##获取scaleTitle级别配置(清洗后)

    def scale(self):
        ##获取scale坐标范围
        scaleCoordinate = self.value.scaleConf["coordinate"]

        ##判断scale是否存在
        if scaleCoordinate.STATUS:  ##若不存在
            return None

        if self.value.scaleConf["setNull"]:
            self.setValue(scaleCoordinate, np.nan)
            return None

        if self.value.scaleConf["setValue"] != False:
            self.setValue(scaleCoordinate, self.value.scaleConf["setValue"])

        ##获取scale级别
        self.value.scaleData = self.value.sheetData.iloc[
            scaleCoordinate.start[0] - 1: scaleCoordinate.start[0] + scaleCoordinate.rows - 1,
            scaleCoordinate.start[1] - 1: scaleCoordinate.start[1] + scaleCoordinate.columns - 1
        ]

        ##整个单元格匹配才替换
        for replaceAll in self.value.scaleConf["replaceAll"]:
            if "iniData" in replaceAll and "data" in replaceAll:
                self.value.scaleData[self.value.scaleData == replaceAll["iniData"]] = replaceAll["data"]

        ##单元格内匹配就替换
        for replaceSome in self.value.scaleConf["replaceSome"]:
            if "iniData" in replaceSome and "data" in replaceSome:
                self.iniData = replaceSome["iniData"] if isinstance(replaceSome["iniData"], str) else str(replaceSome["iniData"])
                self.data = replaceSome["data"] if isinstance(replaceSome["data"], str) else str(replaceSome["data"])
                for i in range(scaleCoordinate.start[0] - 1, scaleCoordinate.start[0] + scaleCoordinate.rows - 1):
                    for j in range(scaleCoordinate.start[1] - 1,scaleCoordinate.start[1] + scaleCoordinate.columns - 1):
                        cell = self.value.sheetData.iloc[i, j]
                        if not isinstance(cell, str): cell = str(cell)
                        self.value.sheetData.iloc[i, j] = self.replaceSome(cell)

        ##调整日期格式
        if self.value.scaleConf["isDateFormat"]:
            self.targetFormat = self.value.scaleConf["dateFormat"]["targetFormat"] ##目标格式
            for i in range(scaleCoordinate.start[0] - 1, scaleCoordinate.start[0] + scaleCoordinate.rows - 1):
                for j in range(scaleCoordinate.start[1] - 1, scaleCoordinate.start[1] + scaleCoordinate.columns - 1):
                    date = self.value.sheetData.iloc[i, j]
                    if date != date:
                        continue
                    if not isinstance(date, str): date = str(date)
                    self.value.sheetData.iloc[i, j] = self.dateFormat(date)

        ##填充合并单元格
        ##单行填充
        if self.value.scaleConf["fillRows"]:
            self.fillRows(scaleCoordinate)
        ##单列填充
        if self.value.scaleConf["fillColumns"]:
            self.fillColumns(scaleCoordinate)

    def setValue(self, scaleCoordinate, value):
        """
        设为指定值
        """
        self.value.sheetData.iloc[
            scaleCoordinate.start[0] - 1: scaleCoordinate.start[0] + scaleCoordinate.rows - 1,
            scaleCoordinate.start[1] - 1: scaleCoordinate.start[1] + scaleCoordinate.columns - 1
        ] = value

    def fillRows(self, scaleCoordinate):
        """
        单行填充
        """
        for i in range(scaleCoordinate.start[0] - 1, scaleCoordinate.start[0] + scaleCoordinate.rows - 1):
            flag = 0  ##是否处于空值填充范围
            preThis = -1;
            this = -1  ##当前坐标与上一个坐标
            start = -1;
            end = -1  ##开始与结束范围
            value = None
            for j in range(scaleCoordinate.start[1] - 1, scaleCoordinate.start[1] + scaleCoordinate.columns - 1):
                preThis = this;
                this = j
                if flag == 1:  ##若处于空值填充范围
                    if self.value.sheetData.iloc[i, j] == self.value.sheetData.iloc[i, j]:  # 若不是空值
                        end = preThis

                        ##补充操作,替换空值
                        self.value.sheetData.iloc[i,start + 1: end + 1] = value

                        start = this
                        value = self.value.sheetData.iloc[i, j]
                        flag = 0
                else:
                    if self.value.sheetData.iloc[i, j] == self.value.sheetData.iloc[i, j]:  # 若不是空值
                        start = this
                        value = self.value.sheetData.iloc[i, j]
                    else:
                        flag = 1

            if flag == 1:
                ##补充操作,替换空值
                y = scaleCoordinate.start[1] + scaleCoordinate.columns - 1
                self.value.sheetData.iloc[i, start+1:y] = value

    def fillColumns(self, scaleCoordinate):
        """
        单列填充
        """
        for i in range(scaleCoordinate.start[1] - 1, scaleCoordinate.start[1] + scaleCoordinate.columns -1):
            flag = 0  ##是否处于空值填充范围
            preThis = -1;
            this = -1  ##当前坐标与上一个坐标
            start = -1;
            end = -1  ##开始与结束范围
            value = None
            for j in range(scaleCoordinate.start[0] - 1, scaleCoordinate.start[0] + scaleCoordinate.rows -1):
                preThis = this;
                this = j
                if flag == 1:  ##若处于空值填充范围
                    if self.value.sheetData.iloc[j, i] == self.value.sheetData.iloc[j, i]:  # 若不是空值
                        end = preThis

                        ##补充操作,替换空值
                        self.value.sheetData.iloc[start + 1: end + 1, i] = value

                        start = this
                        value = self.value.sheetData.iloc[j, i]
                        flag = 0
                else:
                    if self.value.sheetData.iloc[j, i] == self.value.sheetData.iloc[j, i]:  # 若不是空值
                        start = this
                        value = self.value.sheetData.iloc[j, i]
                    else:
                        flag = 1

            if flag == 1:
                ##补充操作,替换空值
                x = scaleCoordinate.start[0] + scaleCoordinate.rows - 1
                self.value.sheetData.iloc[start + 1: x, i] = value

    def replaceSome(self, cell):
        if not isinstance(cell, str):
            cell = str(cell)

        cell = cell.replace(self.iniData, self.data)
        return cell

    def dateFormat(self, date):
        """
        日期转换
        """
        ##尝试使用格式转换
        if not isinstance(date, str):
            date = str(date)

        for dateFormat in self.value.scaleConf["dateFormat"]["format"]:
            try:
                date = timeTool.dateToStr(timeTool.strToDate(date, dateFormat), self.targetFormat)
                return date
            except Exception:
                pass

        ##尝试使用自定义转换器转换
        for dateFormat in self.value.scaleConf["dateFormat"]["dateFormat"]:
            try:
                date = self.value.dateFormatFunc[dateFormat](date, self.targetFormat)
                return date
            except Exception as e:
                pass

        if self.value.scaleConf["dateFormat"]["isEmptyWhenFalse"]:
            return ""
        else:
            return date
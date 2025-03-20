# -*- coding:utf8 -*-
"""
##执行mainTitle级别转换
"""
from . import cheakConf, scale
from .com.util.coordinate import coordinate
from .com.util import excelTool

class mainTitle:
    def __init__(self, value, conf):

        """
        mainTitle级别操作
        :param value: 变量文件
        :param conf: mainTitle级别配置（清洗前）
        """
        self.value = value
        cheakConf.mainTitleConf(self.value, conf) ##获取mainTitle级别配置(清洗后)

    def mainTitle(self):
        ##初始化mainTitle坐标集
        mainTitleCoord = coordinate(self.value.mainTitlePosition)
        ##判断标题行是否存在
        if mainTitleCoord.STATUS: ##若不存在
            for i in range(mainTitleCoord.columns): ##生成临时字段名
                self.value.columnsType["columns"+str(i)] = "str"
            return None

        ##若标题行存在
        ##将所有标题转换为字符串
        for i in range(mainTitleCoord.start[0] - 1, mainTitleCoord.start[0] + mainTitleCoord.rows - 1):
            for j in range(mainTitleCoord.start[1] - 1, mainTitleCoord.start[1] + mainTitleCoord.columns - 1):
                if self.value.sheetData.iloc[i,j] != self.value.sheetData.iloc[i,j]:
                    self.value.sheetData.iloc[i, j] = ""
                elif not isinstance(self.value.sheetData.iloc[i,j], str):
                    self.value.sheetData.iloc[i,j] = str(self.value.sheetData.iloc[i,j])

        ##调整scale级别
        if "scaleList" in self.value.mainTitleConfDown:
            scaleConfList = cheakConf.combinScaleConf(self.value, self.value.mainTitleConfDown["scaleList"], self.value.mainTitleConfDown, self.value.mainTitlePosition, mainTitleCoord)  ##scale级别配置文件合并
            for scaleConf in scaleConfList:
                scaleManager = scale.scale(self.value, scaleConf)
                scaleManager.scale()

        ##获取mainTitle级别数据
        self.value.mainTitleData = self.value.sheetData.iloc[
                                mainTitleCoord.start[0] - 1: mainTitleCoord.start[0] + mainTitleCoord.rows - 1,
                                mainTitleCoord.start[1] - 1: mainTitleCoord.start[1] + mainTitleCoord.columns - 1
                                ]

        ##获取标题字段配置
        titleColumnConf = self.value.mainTitleConf["titleList"].copy()
        titleColumnConfTemp = []
        titleNameDic = {}
        for titleColumn in titleColumnConf:
            if "titleName" in titleColumn:
                titleNameDic[titleColumn["titleName"]] = titleColumn["columnName"] if "columnName" in titleColumn else ""
            else:
                titleColumnConfTemp.append(titleColumn)

        titleColumnConf = titleColumnConfTemp
        titleColumnConfTemp = []
        titleIndexDic = {}
        for titleColumn in titleColumnConf:
            if "titleIndex" in titleColumn:
                titleIndexDic[titleColumn["titleIndex"]] = titleColumn["columnName"] if "columnName" in titleColumn else ""
            else:
                titleColumnConfTemp.append(titleColumn)

        titleColumnConf = titleColumnConfTemp
        titleColumnConfTemp = []
        titleLetterDic = {}
        for titleColumn in titleColumnConf:
            if "titleLetter" in titleColumn:
                titleLetterDic[titleColumn["titleLetter"]] = titleColumn["columnName"] if "columnName" in titleColumn else ""
            else:
                titleColumnConfTemp.append(titleColumn)

        ##形成columnsType
        mainColumnIndex=[]
        for i in self.value.mainColumnIndex:
            code = excelTool.numberToLetter(i+1) ##数字转字母
            title = ""
            for j in self.value.titleRowIndex:
                a = self.value.sheetData.iloc[j, i]
                if a != a:  ##判断是否为nan值
                    title += ''
                elif not isinstance(a, str):
                    title += str(a)
                else:
                    title += a

            if title in self.value.columnsType or title == "":
                index = 0
                while True:
                    index += 1
                    titleTemp = title + "_" + str(index)
                    if titleTemp not in self.value.columnsType:
                        break
                title = titleTemp

            if title in titleNameDic:
                title = titleNameDic[title] if titleNameDic[title] != "" else title
            elif i in titleIndexDic:
                title = titleIndexDic[i] if titleIndexDic[i] != "" else title
            elif code in titleLetterDic:
                title = titleLetterDic[code] if titleLetterDic[code] != "" else title
            elif not self.value.mainTitleConf["readAllTitle"]: ##若没有命中配置，且不读取所有标题，则该列标题跳过
                continue

            self.value.columnsType[title] = ["str", i]
            mainColumnIndex.append(i)

        self.value.mainColumnIndex = mainColumnIndex
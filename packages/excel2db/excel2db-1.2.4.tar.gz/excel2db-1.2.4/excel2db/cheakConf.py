# -*- coding:utf8 -*-
"""
生成对应级别配置文件
"""
from json import loads
from .com.util import fileTool, coordinate, excelTool
from . import defaultConf

def combinExcelConf(*configFileUrl):
    """
    校验配置文件，并合并excel级别配置文件，后面的配置文件覆盖前面的
    :param conf: 配置文件元组
    """
    filetool = fileTool.fileTool()
    conf = []
    for i in configFileUrl:
        if isinstance(i, dict): ##尝试作为python字典读取
            conf.append(i)
        else:
            try:  ##尝试作为json读取
                data = loads(i)
                conf.append(data)
            except Exception:
                try:  ##尝试作为路径读取
                    data = filetool.readAllFile(i)
                    data = loads(data)
                    conf.append(data)
                except Exception:
                    raise Exception(f"读取配置文件'{i}'失败")

    ##校验配置文件
    for i in conf:
        flag, info = cheakConf(i, "excel")

        if flag:
            raise Exception(f"配置文件出错:{info}")

    ##合并配置文件
    confNew = {}
    for i in conf:
        for item in i:
            if item == "sheet":
                if "sheet" not in confNew:
                    confNew["sheet"] = []
                for j in i["sheet"]:
                    confNew["sheet"].append(j)
            else:
                confNew[item] = returnTrue(i[item])

    return confNew

def cheakConf(conf, level): ##待完善
    """
    简单校验各个级别配置文件
    :param conf:校验配置文件数据
    :param level:当前配置文件级别
    :return: flag: 1为错，0为正确
    :return: info:
    """
    def verityTypeFromDefaultConfig(conf, defaultConf):
        """
        利用默认配置文件校验配置文件
        :param conf:
        :param defaultConf:
        :return:
        """
        flag = 0
        info = ""
        for item in defaultConf:
            if item in conf:
                if not isinstance(conf[item], type(defaultConf[item])):
                    flag = 1
                    info = f"字段{item}错误"
                    break
        return flag, info

    flag = 0
    info = ""
    if level == "excel":
        flagIn, infoIn = verityTypeFromDefaultConfig(conf, defaultConf.excel)
        if flagIn: ##若excel级别有问题
            flag = flagIn
            info = infoIn
        else:
            if "sheet" in conf: ##若"sheet"级别配置存在
                for i in conf["sheet"]:
                    flagIn, infoIn = cheakConf(i, "sheet")
                    if flagIn:  ##若sheet级别有问题
                        flag = flagIn
                        info = "sheet/" + infoIn
                        break

    elif level == "sheet":
        flagIn, infoIn = verityTypeFromDefaultConfig(conf, defaultConf.excel)
        if flagIn:  ##若sheet级别有问题
            flag = flagIn
            info = infoIn
        else:
            if flag != 1 and "mainTitle" in conf:  ##若"mainTitle"级别配置存在
                flagIn, infoIn = cheakConf(conf["mainTitle"], "mainTitle")
                if flagIn:  ##若mainTitle级别有问题
                    flag = flagIn
                    info = "sheet/" + infoIn
            if flag != 1 and "mainData" in conf:  ##若"mainData"级别配置存在
                flagIn, infoIn = cheakConf(conf["mainData"], "mainData")
                if flagIn:  ##若mainData级别有问题
                    flag = flagIn
                    info = "sheet/" + infoIn
            if flag != 1 and "detailTitle" in conf:  ##若"detailTitle"级别配置存在
                flagIn, infoIn = cheakConf(conf["detailTitle"], "detailTitle")
                if flagIn:  ##若detailTitle级别有问题
                    flag = flagIn
                    info = "sheet/" + infoIn
            if flag != 1 and "detailData" in conf:  ##若"detailData"级别配置存在
                flagIn, infoIn = cheakConf(conf["detailData"], "detailData")
                if flagIn:  ##若detailData级别有问题
                    flag = flagIn
                    info = "sheet/" + infoIn

    elif level == "mainTitle":
        flagIn, infoIn = verityTypeFromDefaultConfig(conf, defaultConf.mainTitle)
        if flagIn:  ##若mainTitle级别有问题
            flag = flagIn
            info = infoIn
        else:
            if "scale" in conf:  ##若"scale"级别配置存在
                for i in conf["scale"]:
                    flagIn, infoIn = cheakConf(i, "scale")
                    if flagIn:  ##若sheet级别有问题
                        flag = flagIn
                        info = "mainTitle/" + infoIn
                        break

    elif level == "mainData":
        flagIn, infoIn = verityTypeFromDefaultConfig(conf, defaultConf.mainData)
        if flagIn:  ##若mainData级别有问题
            flag = flagIn
            info = infoIn
        else:
            if "scale" in conf:  ##若"scale"级别配置存在
                for i in conf["scale"]:
                    flagIn, infoIn = cheakConf(i, "scale")
                    if flagIn:  ##若sheet级别有问题
                        flag = flagIn
                        info = "mainData/" + infoIn
                        break

    elif level == "detailTitle":
        flagIn, infoIn = verityTypeFromDefaultConfig(conf, defaultConf.detailTitle)
        if flagIn:  ##若detailTitle级别有问题
            flag = flagIn
            info = infoIn
        else:
            if "scale" in conf:  ##若"scale"级别配置存在
                for i in conf["scale"]:
                    flagIn, infoIn = cheakConf(i, "scale")
                    if flagIn:  ##若sheet级别有问题
                        flag = flagIn
                        info = "detailTitle/" + infoIn
                        break


    elif level == "detailData":
        flagIn, infoIn = verityTypeFromDefaultConfig(conf, defaultConf.detailData)
        if flagIn:  ##若detailData级别有问题
            flag = flagIn
            info = infoIn
        else:
            if "scale" in conf:  ##若"scale"级别配置存在
                for i in conf["scale"]:
                    flagIn, infoIn = cheakConf(i, "scale")
                    if flagIn:  ##若sheet级别有问题
                        flag = flagIn
                        info = "detailData/" + infoIn
                        break

    elif level == "scale":
        flagIn, infoIn = verityTypeFromDefaultConfig(conf, defaultConf.scale)
        if flagIn:  ##若detailData级别有问题
            flag = flagIn
            info = infoIn

    else:
        pass
    return flag, info

def excelConf(value, conf):
    """
    :param conf: excel级别配置文件（清洗前）
    """
    confTemp = {}

    for item in defaultConf.excel:
        if item in conf: ##若配置则使用配置的值
            confTemp[item] = returnTrue(conf[item])
        else: ##若未配置则使用默认值
            confTemp[item] = returnTrue(defaultConf.excel[item])

    value.excelConf = confTemp

    confTempDown = {}  ##向下配置文件

    for item in conf:
        if item not in defaultConf.excel: ##若不属于当前级别配置文件
            confTempDown[item] = returnTrue(conf[item])

    value.excelConfDown = confTempDown

def combinSheetConf(value):
    """
    合并sheet级别配置文件
    :return: confTemp : 返回合并后的sheet级别配置文件列表
    """
    def fill(value, excelConfDown):
        """
        补全sheetID和sheetname
        :param excelConfDown: excel级别向下的配置
        :return:
        """
        confTemp = []
        for sheetConf in excelConfDown["sheet"]:
            if "sheetID" not in sheetConf and "sheetName" not in sheetConf:
                continue

            if "sheetName" in sheetConf:
                if sheetConf["sheetName"] in value.sheetList:
                    sheetID = value.sheetList.index(sheetConf["sheetName"])
                    sheetConf["sheetID"] = sheetID
                    confTemp.append(sheetConf.copy())
                    continue

            else:
                if sheetConf["sheetID"] >= 0 and sheetConf["sheetID"] < len(value.sheetList): ##若为正数
                    sheetConf["sheetName"] = value.sheetList[sheetConf["sheetID"]]
                    confTemp.append(sheetConf.copy())
                elif sheetConf["sheetID"] < 0 and (sheetConf["sheetID"] + len(value.sheetList)) >= 0: ##若为负数
                    sheetConf["sheetID"] = sheetConf["sheetID"] + len(value.sheetList)
                    sheetConf["sheetName"] = value.sheetList[sheetConf["sheetID"]]
                    confTemp.append(sheetConf.copy())

        return confTemp



    if value.excelConf["readAllSheet"]:
        if "sheet" in value.excelConfDown:
            confTemp = fill(value, value.excelConfDown)
            for sheetID, sheetName in enumerate(value.sheetList):
                a = 1
                for j in confTemp:
                    if sheetID == j["sheetName"]:
                        a = 0
                        break
                if a == 1:  ##若未配置，则将sheet表以默认形式读入
                    confTemp.append({
                        "sheetID": sheetID,
                        "sheetName": sheetName
                    })
        else:
            confTemp = []
            for sheetID, sheetName in enumerate(value.sheetList):
                confTemp.append({
                    "sheetID": sheetID,
                    "sheetName": sheetName
                })

    else:
        if "sheet" in value.excelConfDown:
            confTemp = fill(value, value.excelConfDown)
        else:
            return []

    ##生成字典，key为sheetID，value为sheet配置文件列表
    confDic = {}
    for sheetConf in confTemp:
        if sheetConf["sheetID"] not in confDic:
            confDic[sheetConf["sheetID"]] = []
        confDic[sheetConf["sheetID"]].append(sheetConf)

    ##对sheetID相同的配置文件进行合并
    conf = []
    for sheetID in confDic:
        conf.append(confDic[sheetID][0])

    ##此处向下继承操作待完善
    for sheetConf in conf:
        for i in value.excelConfDown:
            if i not in sheetConf and i != 'sheet':
                sheetConf[i] = returnTrue(value.excelConfDown[i])

    return conf

def sheetConf(value, conf):
    """
    :param conf: sheet级别配置文件（清洗前）
    """
    confTemp = {}

    for item in defaultConf.sheet:
        if item in conf: ##若配置则使用配置的值
            confTemp[item] = returnTrue(conf[item])
        else: ##若未配置则使用默认值
            confTemp[item] = returnTrue(defaultConf.sheet[item])

    value.sheetConf = confTemp

    confTempDown = {}  ##向下配置文件

    for item in conf:
        if item not in defaultConf.sheet: ##若不属于当前级别配置文件
            confTempDown[item] = returnTrue(conf[item])

    value.sheetConfDown = confTempDown

def combinMainTitleConf(value):
    """
    合并mainTitle级别配置文件
    :return: confTemp : 返回合并后的mainTitle级别配置文件列表
    """
    ##合并操作在sheet级别进行
    pass
    ##向下继承操作

    if "mainTitle" not in value.sheetConfDown:
        confTemp = {}
    else:
        confTemp = value.sheetConfDown["mainTitle"].copy()

    for i in value.sheetConfDown:
        if i not in confTemp and i not in ('mainTitle', "mainData", "detailTitle", "detailData"):
                confTemp[i] = returnTrue(value.sheetConfDown[i])

    return confTemp

def mainTitleConf(value, conf):
    """
    :param conf: mainTitle级别配置文件（清洗前）
    """
    confTemp = {}

    for item in defaultConf.mainTitle:
        if item in conf: ##若配置则使用配置的值
            confTemp[item] = returnTrue(conf[item])
        else: ##若未配置则使用默认值
            confTemp[item] = returnTrue(defaultConf.mainTitle[item])

    value.mainTitleConf = confTemp

    confTempDown = {}  ##向下配置文件

    for item in conf:
        if item not in defaultConf.mainTitle: ##若不属于当前级别配置文件
            confTempDown[item] = returnTrue(conf[item])

    value.mainTitleConfDown = confTempDown


def combinMainDataConf(value):
    """
    合并mainData级别配置文件
    :return: confTemp : 返回合并后的mainData级别配置文件列表
    """
    ##合并操作在sheet级别进行
    pass
    ##向下继承操作

    if "mainData" not in value.sheetConfDown:
        confTemp = {}
    else:
        confTemp = value.sheetConfDown["mainData"].copy()

    for i in value.sheetConfDown:
        if i not in confTemp and i not in ('mainTitle', "mainData", "detailTitle", "detailData"):
            confTemp[i] = returnTrue(value.sheetConfDown[i])

    return confTemp

def mainDataConf(value, conf):
    """
    :param conf: mainData级别配置文件（清洗前）
    """
    confTemp = {}

    for item in defaultConf.mainData:
        if item in conf: ##若配置则使用配置的值
            confTemp[item] = returnTrue(conf[item])
        else: ##若未配置则使用默认值
            confTemp[item] = returnTrue(defaultConf.mainData[item])

    value.mainDataConf = confTemp

    confTempDown = {}  ##向下配置文件

    for item in conf:
        if item not in defaultConf.mainData: ##若不属于当前级别配置文件
            confTempDown[item] = returnTrue(conf[item])

    value.mainDataConfDown = confTempDown


def combindetailTitleConf(value):
    """
    合并detailTitle级别配置文件
    :return: confTemp : 返回合并后的detailTitle级别配置文件列表
    """
    ##合并操作在sheet级别进行
    pass
    ##向下继承操作

    if "detailTitle" not in value.sheetConfDown:
        confTemp = {}
    else:
        confTemp = value.sheetConfDown["detailTitle"].copy()

    for i in value.sheetConfDown:
        if i not in confTemp and i not in ('mainTitle', "mainData", "detailTitle", "detailData"):
            confTemp[i] = returnTrue(value.sheetConfDown[i])

    return confTemp

def detailTitleConf(value, conf):
    """
    :param conf: detailTitle级别配置文件（清洗前）
    """
    confTemp = {}

    for item in defaultConf.detailTitle:
        if item in conf: ##若配置则使用配置的值
            confTemp[item] = returnTrue(conf[item])
        else: ##若未配置则使用默认值
            confTemp[item] = returnTrue(defaultConf.detailTitle[item])

    value.detailTitleConf = confTemp

    confTempDown = {}  ##向下配置文件

    for item in conf:
        if item not in defaultConf.detailTitle: ##若不属于当前级别配置文件
            confTempDown[item] = returnTrue(conf[item])

    value.detailTitleConfDown = confTempDown

def combindetailDataConf(value):
    """
    合并detailData级别配置文件
    :return: confTemp : 返回合并后的detailData级别配置文件列表
    """
    ##合并操作在sheet级别进行
    pass
    ##向下继承操作

    if "detailData" not in value.sheetConfDown:
        confTemp = {}
    else:
        confTemp = value.sheetConfDown["detailData"].copy()

    for i in value.sheetConfDown:
        if i not in confTemp and i not in ('mainTitle', "mainData", "detailTitle", "detailData"):
            confTemp[i] = returnTrue(value.sheetConfDown[i])

    return confTemp

def detailDataConf(value, conf):
    """
    :param conf: detailData级别配置文件（清洗前）
    """
    confTemp = {}

    for item in defaultConf.detailData:
        if item in conf: ##若配置则使用配置的值
            confTemp[item] = returnTrue(conf[item])
        else: ##若未配置则使用默认值
            confTemp[item] = returnTrue(defaultConf.detailData[item])

    value.detailDataConf = confTemp

    confTempDown = {}  ##向下配置文件

    for item in conf:
        if item not in defaultConf.detailData: ##若不属于当前级别配置文件
            confTempDown[item] = returnTrue(conf[item])

    value.detailDataConfDown = confTempDown

def combinScaleConf(value, scaleList, confDown, upPosition, upCoordinate):
    """
    合并scale级别配置文件
    :param scaleList: 范围列表
    :param confDown: 向下继承文件
    :param upPosition: 上一级四边定位
    :param upCoordinate: 上一级坐标范围
    :return: 返回合并后的scale级别配置文件列表
    """
    ##向下继承操作,并获取坐标范围
    confTemp = [] ##存储继承后的scaleList
    for scaleConf in scaleList:
        scaleCoordinate = [-1,-1,-1,-1] ##当前范围的四边定位
        for i in confDown:
            if i not in scaleConf and i != "scaleList":
                scaleConf[i] = returnTrue(confDown[i])

        ##补全四边定位
        if "start" in scaleConf:
            scaleCoordinate[0], scaleCoordinate[2] = excelTool.letterToNumber(scaleConf["start"])
        else:
            scaleCoordinate[0], scaleCoordinate[2] = upPosition[0], upPosition[2]

        if "rows" in scaleConf:
            if scaleConf["rows"] == 0:
                scaleCoordinate[1] = upPosition[1]
            else:
                scaleCoordinate[1] = scaleCoordinate[0] + scaleConf["rows"] - 1
        else:
            scaleCoordinate[1] = upPosition[1]

        if "columns" in scaleConf:
            if scaleConf["columns"] == 0:
                scaleCoordinate[3] = upPosition[3]
            else:
                scaleCoordinate[3] = scaleCoordinate[2] + scaleConf["columns"] - 1
        else:
            scaleCoordinate[3] = upPosition[3]

        ##获取坐标范围
        scaleConf["coordinate"] = coordinate.coordinate(scaleCoordinate)
        if scaleConf["coordinate"].STATUS:
            continue

        scaleConf["coordinate"] = scaleConf["coordinate"] + upCoordinate

        ##分割坐标范围
        indexList = []
        for index, scaleConfTemp in enumerate(confTemp):
            scaleConfTemp["coordinate"] = scaleConfTemp["coordinate"] - scaleConf["coordinate"]
            if scaleConfTemp["coordinate"].STATUS:
                indexList.append(index)

        confTemp.append(scaleConf)

        ##去除空范围
        length = len(indexList)
        for i in range(length):
            confTemp.pop(indexList[-1])
            indexList = indexList[:-1]

    return confTemp

def scaleConf(value, conf):
    """
    :param conf: scaleData级别配置文件（清洗前）
    """
    confTemp = {}

    for item in defaultConf.scale:
        if item in conf: ##若配置则使用配置的值
            confTemp[item] = returnTrue(conf[item])

            if item in ("dateFormat"):
                for itemIn in defaultConf.scale[item]:
                    if itemIn in conf[item]:  ##若配置则使用配置的值
                        confTemp[item][itemIn] = returnTrue(conf[item][itemIn])
                    else:  ##若未配置则使用默认值
                        confTemp[item][itemIn] = returnTrue(defaultConf.scale[item][itemIn])
        else: ##若未配置则使用默认值
            confTemp[item] = returnTrue(defaultConf.scale[item])



    confTemp["coordinate"] = returnTrue(conf["coordinate"])

    value.scaleConf = confTemp

def returnTrue(obj):
    """
    判断是否为序列类型,并返回一个全新变量
    :param obj:
    :return:
    """
    if isinstance(obj, list) or isinstance(obj, set) or isinstance(obj, dict):
        return obj.copy()
    else:
        return obj

if __name__ == "__main__":
    a = cheakConf(defaultConf.test, defaultConf)
    print(a)
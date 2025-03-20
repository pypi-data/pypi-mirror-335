
"""
日期格式化演示
"""
from excel2db.excel2db import excel2db
from excel2db.com.util import timeTool

def dateFormat_1(date, targetFormat):
    """
    自定义日期格式化方法
    :param date: 传入日期
    :param targetFormat:目标格式
    :return: 返回日期
    """
    baseDate = "2023-08-01"  ##基准日期
    baseNum = 45139  ##基准数字
    number = int(float(date))
    date = timeTool.changeTime(baseDate, "days", number - baseNum, targetFormat)

    return date

if __name__ == "__main__":
    excelUrl = "./demo10.xlsx"
    ed = excel2db("./demo10.json")
    ed.setDateFormatFunc(dateFormat_1)
    ed.excel2db(excelUrl)
    ed.getDBConnect().close()
        
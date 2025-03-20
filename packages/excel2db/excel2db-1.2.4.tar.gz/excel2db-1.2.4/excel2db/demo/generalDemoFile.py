
demo = {
    "demo1":{
        "file":"""
\"\"\"
快速演示
\"\"\"
from excel2db.excel2db import excel2db

if __name__ == "__main__":
    excelUrl = "./demo1.xlsx"
    ed = excel2db()
    ed.excel2db(excelUrl)
    ed.getDBConnect().close()
        """,
        "json":"",
        "excel":[
            {
                "sheetName":"st1",
                "data":[
                    ["姓名","性别"],
                    ["张三","男"],
                    ["李四","女"]
                ]
            }
        ]
    },
    "demo2":{
        "file":"""
\"\"\"
无标题文件
\"\"\"
from excel2db.excel2db import excel2db

if __name__ == "__main__":
    excelUrl = "./demo2.xlsx"
    ed = excel2db("./demo2.json")
    ed.excel2db(excelUrl)
    ed.getDBConnect().close()
        """,
        "json":"""
{
  "sheet" : [
    {
      "sheetID" : 0,
      "titleLines" : 0
    }
  ]
}
        """,
        "excel":[
            {
                "sheetName":"st1",
                "data":[
                    ["张三","男"],
                    ["李四","女"]
                ]
            }
        ]
    },
    "demo3":{
        "file":"""
\"\"\"
明细表示例
\"\"\"
from excel2db.excel2db import excel2db

if __name__ == "__main__":
    excelUrl = "./demo3.xlsx"
    ed = excel2db("./demo3.json")
    ed.excel2db(excelUrl)
    ed.getDBConnect().close()
        """,
        "json":"""
{
  "sheet" : [
    {
      "sheetID" : 0,
      "isIncludeDetail" : true,
      "detailSplitByColumnID" : "C",
      "detailTitle": {
        "detailTitleName":[
          "科目"
        ]
      }
    }
  ]
}
        """,
        "excel":[
            {
                "sheetName":"st1",
                "data":[
                    ["姓名","性别","语文","数学","英语"],
                    ["张三","男",56,67,76],
                    ["李四","女",45,34,54]
                ]
            }
        ]
    },
    "demo4":{
        "file":"""
\"\"\"
多sheet演示
\"\"\"
from excel2db.excel2db import excel2db

if __name__ == "__main__":
    excelUrl = "./demo4.xlsx"
    ed = excel2db()
    ed.excel2db(excelUrl)
        """,
        "json":"""
        """,
        "excel":[
            {
                "sheetName":"st1",
                "data":[
                    ["姓名","性别"],
                    ["张三","男"],
                    ["李四","女"]
                ]
            },
            {
                "sheetName": "st2",
                "data": [
                    ["课程", "分数"],
                    ["语文", 34],
                    ["数学", 43]
                ]
            }
        ]
    },
    "demo5":{
        "file":"""
\"\"\"
多sheet演示(2)
\"\"\"
from excel2db.excel2db import excel2db

if __name__ == "__main__":
    excelUrl = "./demo5.xlsx"
    ed = excel2db("./demo5.json")
    ed.excel2db(excelUrl)
    ed.getDBConnect().close()
        """,
        "json":"""
{
  "readAllSheet" : false,
  "sheet" : [
    {
      "sheetID" : 0
    },
    {
      "sheetName" : "st2"
    },
    {
      "sheetID" : -1
    }
  ]
}
        """,
        "excel":[
            {
                "sheetName":"st1",
                "data":[
                    ["姓名","性别"],
                    ["张三","男"],
                    ["李四","女"]
                ]
            },
            {
                "sheetName": "st2",
                "data": [
                    ["课程", "分数"],
                    ["语文", 34],
                    ["数学", 43]
                ]
            },
            {
                "sheetName": "st3",
                "data": [
                    ["课程", "分数"],
                    ["语文", 34],
                    ["数学", 43]
                ]
            },
            {
                "sheetName": "st4",
                "data": [
                    ["课程", "分数"],
                    ["语文", 34],
                    ["数学", 43]
                ]
            }
        ]
    },
    "demo6":{
        "file":"""
\"\"\"
读取字段配置演示
\"\"\"
from excel2db.excel2db import excel2db

if __name__ == "__main__":
    excelUrl = "./demo6.xlsx"
    ed = excel2db("./demo6.json")
    ed.excel2db(excelUrl)
    ed.getDBConnect().close()
        """,
        "json":"""
{
  "datLoad" : "./test.db",
  "sheet" : [
    {
      "sheetID" : 0,
      "mainTitle": {
        "readAllTitle": false,
        "titleList" : [
          {
            "titleName" : "性别",
            "columnName": "sex"
          },{
            "titleIndex" : 0,
            "columnName": "name"
          },{
            "titleLetter": "C",
            "columnName": "age"
          }
        ]
      }
    }
  ]
}
        """,
        "excel":[
            {
                "sheetName":"st1",
                "data":[
                    ["姓名","性别","年龄","爱好"],
                    ["张三","男",23,"篮球"],
                    ["李四","女",21,"足球"]
                ]
            }
        ]
    },
    "demo7":{
        "file":"""
\"\"\"
获取数据演示
\"\"\"
from excel2db.excel2db import excel2db
from excel2db.com.util import dbconnect

if __name__ == "__main__":
    excelUrl = "./demo7.xlsx"
    ed = excel2db()
    ed.excel2db(excelUrl)

    ##获取列表
    print("获取列表")
    sql = 'SELECT id, "姓名" AS name, "性别" AS sex, "年龄" AS age FROM "st1"'
    ed.getDBConnect().cursor.execute(sql)
    for row in ed.value.dbConnect.cursor.fetchall():
        print(row)

    selectData = dbconnect.selectData(ed.value.dbConnect, sql)
    print("获取字段名")
    print(selectData.columns)
    print("获取列表")
    for row in selectData.dataByRow:
        print(row.toLis())
    print("获取字典")
    for row in selectData.dataByRow:
        print(row.toDic())

    ed.getDBConnect().close()
        """,
        "json":"""
        """,
        "excel":[
            {
                "sheetName":"st1",
                "data":[
                    ["姓名","性别","年龄","爱好"],
                    ["张三","男",23,"篮球"],
                    ["李四","女",21,"足球"]
                ]
            }
        ]
    },
    "demo8":{
        "file":"""
\"\"\"
每三行只获取一行演示
\"\"\"
from excel2db.excel2db import excel2db

if __name__ == "__main__":
    excelUrl = "./demo8.xlsx"
    ed = excel2db("./demo8.json")
    ed.excel2db(excelUrl)
    ed.getDBConnect().close()
        """,
        "json":"""
{
  "sheet" : [
    {
      "sheetID" : 0,
      "mainData" : {
        "mainDataRows" : ["row%2==1"]
      }
    }
  ]
}
        """,
        "excel":[
            {
                "sheetName":"st1",
                "data":[
                    ["行数"],
                    ["第一行"],
                    ["第二行"],
                    ["第三行"],
                    ["第四行"],
                    ["第五行"],
                    ["第六行"]
                ]
            }
        ]
    },
    "demo9":{
        "file":"""
\"\"\"
任意范围调整演示
\"\"\"
from excel2db.excel2db import excel2db

if __name__ == "__main__":
    excelUrl = "./demo9.xlsx"
    ed = excel2db("./demo9.json")
    ed.excel2db(excelUrl)
    ed.getDBConnect().close()
        """,
        "json":"""
{
  "sheet" : [
    {
      "sheetID" : 0,
      "mainData" : {
        "scaleList" : [
          {
            "start" : "C+2",
            "columns" : 1,
            "replaceAll" : [
              {
                "iniData" : 56,
                "data" : 34
              }
            ]
          },{
            "start" : "D+2",
            "columns" : 1,
            "replaceSome" : [
              {
                "iniData" : 6,
                "data" : 4
              }
            ]
          },{
            "start" : "E+2",
            "columns" : 1,
            "setNull" : true
          },{
            "start" : "F+2",
            "columns" : 1,
            "setValue" : 77
          }
        ]
      }
    }
  ]
}
        """,
        "excel":[
            {
                "sheetName":"st1",
                "data":[
                    ["姓名","性别","语文","数学","英语","历史"],
                    ["张三","男",56,67,76,56],
                    ["李四","女",4565,36,54,89]
                ]
            }
        ]
    },
    "demo10":{
        "file":"""
\"\"\"
日期格式化演示
\"\"\"
from excel2db.excel2db import excel2db
from excel2db.com.util import timeTool

def dateFormat_1(date, targetFormat):
    \"\"\"
    自定义日期格式化方法
    :param date: 传入日期
    :param targetFormat:目标格式
    :return: 返回日期
    \"\"\"
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
        """,
        "json":"""
{
  "sheet" : [
    {
      "sheetID" : 0,
      "mainData" : {
        "scaleList" : [
          {
            "start" : "A+2",
            "columns" : 1,
            "isDateFormat" : true,
            "dateFormat" : {
              "format":[
                "%Y/%m/%d"
              ]
            }
          },{
            "start" : "B+2",
            "columns" : 1,
            "isDateFormat" : true,
            "dateFormat" : {
              "targetFormat" : "%Y-%m-%d",
              "format":[
                "%Y-%m-%d %H:%M:%S"
              ]
            }
          },{
            "start" : "C+2",
            "columns" : 1,
            "isDateFormat" : true,
            "dateFormat" : {
              "targetFormat" : "%Y-%m-%d",
              "dateFormat" : [
                "dateFormat_1"
              ]
            }
          }
        ]
      }
    }
  ]
}
        """,
        "excel":[
            {
                "sheetName":"st1",
                "data":[
                    ["日期1","日期2","日期3"],
                    ["2024/1/2","2024-03-01 01:23:33",45139],
                    ["2023/5/26","2023-02-11 05:56:34",45156]
                ]
            }
        ]
    },
}

from excel2db.com.util import fileTool
import openpyxl
filetool = fileTool.fileTool()

def generalDemoFile():
    for demoName in demo:
        filetool.createDir("./" + demoName, mode=1)
        filetool.writeOverFile("./" + demoName + "/__init__.py", "")
        filetool.writeOverFile("./" + demoName + "/" + demoName + ".py", demo[demoName]["file"])
        filetool.writeOverFile("./" + demoName + "/" + demoName + ".json", demo[demoName]["json"])

        # 生成一个 Workbook 的实例化对象，wb即代表一个工作簿（一个 Excel 文件）
        wb = openpyxl.Workbook()
        index = 1
        for sheet in demo[demoName]["excel"]:
            if index==1:
                ws=wb.active
                ws.title = sheet["sheetName"]
            else:
                wb.create_sheet(sheet["sheetName"])
                ws = wb[sheet["sheetName"]]

            index += 1

            for row in sheet["data"]:
                ws.append(row)

        wb.save("./" + demoName + "/" + demoName + ".xlsx")

if __name__ == "__main__":
    generalDemoFile()

"""
无标题文件
"""
from excel2db.excel2db import excel2db

if __name__ == "__main__":
    excelUrl = "./demo2.xlsx"
    ed = excel2db("./demo2.json")
    ed.excel2db(excelUrl)
    ed.getDBConnect().close()
        
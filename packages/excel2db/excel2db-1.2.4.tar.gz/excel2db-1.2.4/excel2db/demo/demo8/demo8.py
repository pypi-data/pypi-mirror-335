
"""
每三行只获取一行演示
"""
from excel2db.excel2db import excel2db

if __name__ == "__main__":
    excelUrl = "./demo8.xlsx"
    ed = excel2db("./demo8.json")
    ed.excel2db(excelUrl)
    ed.getDBConnect().close()
        
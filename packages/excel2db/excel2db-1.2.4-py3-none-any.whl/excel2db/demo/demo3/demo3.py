
"""
明细表示例
"""
from excel2db.excel2db import excel2db

if __name__ == "__main__":
    excelUrl = "./demo3.xlsx"
    ed = excel2db("./demo3.json")
    ed.excel2db(excelUrl)
    ed.getDBConnect().close()
        
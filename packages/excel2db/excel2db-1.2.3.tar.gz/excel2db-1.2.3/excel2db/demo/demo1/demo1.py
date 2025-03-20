
"""
快速演示
"""
from excel2db.excel2db import excel2db

if __name__ == "__main__":
    excelUrl = "./demo1.xlsx"
    ed = excel2db()
    ed.excel2db(excelUrl)
    ed.getDBConnect().close()
        
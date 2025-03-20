
"""
多sheet演示
"""
from excel2db.excel2db import excel2db

if __name__ == "__main__":
    excelUrl = "./demo4.xlsx"
    ed = excel2db()
    ed.excel2db(excelUrl)
        
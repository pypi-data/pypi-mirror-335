
"""
读取字段配置演示
"""
from excel2db.excel2db import excel2db

if __name__ == "__main__":
    excelUrl = "./demo6.xlsx"
    ed = excel2db("./demo6.json")
    ed.excel2db(excelUrl)
    ed.getDBConnect().close()
        
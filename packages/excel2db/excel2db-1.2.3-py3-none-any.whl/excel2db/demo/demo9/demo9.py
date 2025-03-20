
"""
任意范围调整演示
"""
from excel2db.excel2db import excel2db

if __name__ == "__main__":
    excelUrl = "./demo9.xlsx"
    ed = excel2db("./demo9.json")
    ed.excel2db(excelUrl)
    ed.getDBConnect().close()
        
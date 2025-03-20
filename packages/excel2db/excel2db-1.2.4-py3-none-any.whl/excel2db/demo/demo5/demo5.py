
"""
多sheet演示(2)
"""
from excel2db.excel2db import excel2db

if __name__ == "__main__":
    excelUrl = "./demo5.xlsx"
    ed = excel2db("./demo5.json")
    ed.excel2db(excelUrl)
    ed.getDBConnect().close()
        
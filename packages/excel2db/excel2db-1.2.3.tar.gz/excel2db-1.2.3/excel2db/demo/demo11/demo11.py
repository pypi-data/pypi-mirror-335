
"""
日期格式化演示
"""
from excel2db.excel2db import excel2db

if __name__ == "__main__":
    excelUrl = "./demo11.xlsx"
    ed = excel2db("./demo11.json")
    ed.excel2db(excelUrl)
    sql = "SELECT SQLITE_VERSION()"
    db = ed.getDBConnect()
    db.cursor.execute(sql)
    print(db.cursor.fetchall())
    ##清洗主表数据
    sql = """
            DELETE FROM "we"
    WHERE bref_material_code='nan' OR line='TOTAL' OR bref_material_code LIKE '制造%' OR bref_material_code LIKE '产品%' OR bref_material_code LIKE '白%' OR bref_material_code LIKE '夜%' OR column2='开线数';
            """
    db.cursor.execute(sql)
    ##清明细表数据
    sql = """
            DELETE FROM "we_dt"
    WHERE mainid NOT IN (SELECT id FROM "we") OR value=0 OR value NOT REGEXP '^[0-9]+$';
            """
    db.cursor.execute(sql)
    db.connect.commit()
    ed.getDBConnect().close()
        
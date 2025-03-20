
"""
获取数据演示
"""
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
        
# -*- coding:utf8 -*-
"""
默认配置文件
"""

excel = {
    "isSaveDatabase" : True, ##是否保存到数据库,默认为是
    "dbType" : "sqlite", ##数据库类型，默认为sqlite
    "datLoad" : "", ##生成的数据文件路径，文件名默认为`excel文件名称.db`
    "readAllSheet" : True, ##若为True，读取所有sheet工作表，否则只读取配置的sheet工作表
    "notReadHideSheet" : True, ##若为True,不读取隐藏的工作表，否则都读取
    "password" : "", ##密码
}##下级选项为"sheet" : []
sheet = {  ##sheetid和sheetname二选一,若都为空值，则不生效;若同时存在，则sheetName优先
    "sheetID" : "", ##第几个sheet，0表示第一个sheet，1表示第二个sheet，-1表示最后一个sheet
    "sheetName" : "", ##sheet名称
    "mainPrimaryKey": "id",  ##主表主键名称，默认为id
    "detailPrimaryKey": "id",  ##明细表主键名称，默认为id
    "detailForeignKey": "mainid",  ##明细表外键名称，默认为mainid
    "tableName" : "", ##指定数据库表名,默认为sheet名称
    "tableDtlName" : "", ##指定数据库明细表名,当tableName未指定时，默认为`sheet名称_dt`,当tableName未指定时
    "position": "A+1", ##左上角定位,默认为A+1
    "rows": 0, ##获取指定行数，0表示所有,1表示只获取1行，正数表示获取的行数,-1表示不获取最后1行，负数表示从结尾去除的行数
    "columns": 0, ##获取指定列数，0表示所有,1表示只获取1列,正数表示获取的列数,-1表示不获取最后1列，负数表示从结尾去除的列数
    # "titleInRow" : True, ##标题是否为行，若为行则为True，默认为True
    "titleLines" : 1, ##标题占据的行数或列数，大于等于0，默认为1
    "isIncludeDetail" : False, ##是否包含明细表，默认为False,若为True，需要校验不同时为空，优先选择detailSplitByColumnID
    # "detailSplitByColumnName" : "", ##主表与明细表的分割线，由列名决定，加号左边为固定的行列，加号右边为明细表开始行列
    "detailSplitByColumnID" : "A", ##主表与明细表的分割线，由列编号决定
}##下级选项为"mainTitle" : {}, "mainData" : {}, "detailTitle" : {}, "detailData" : {},
mainTitle = {
    "readAllTitle" : True, ##是否读取所有标题列,若为False，只获取titleList配置中的标题
    # "titleByID" : { ##指定titleID对应的标题名，key为标题对应的编码，A为第一列， value为titleName,此配置优先级大于scaleList，若readAllTitle为True，则只获取配置的标题列
    # },
    "titleList" : [##指定数据库字段名,若配置重复，后面的配置覆盖前面的配置
        {
            "titleName" : "", ##标题名
            "titleIndex" : 0, ##标题序号，0为第一列，1为第二列，-1为最后一列，当配置了titleName时，titleName优先
            "titleLetter": "", ##标题字母，A为第一列，当配置了titleIndex时，titleIndex优先
            "columnName": "" ##数据库字段名，当该配置不存在时，取titleName
        },
    ],
    "titleList" : [] ##默认值为[]，代表获取所有标题列

}##下级选项为"scaleList" : [], ##存储范围调整，靠后的优先级高,具体配置文件参考scale
mainData = { ##注意，主表数据只取配置好的标题中对应的数据
    # "mainDataTypes":{
    #
    # },
    "mainDataRows" : [], ##数据行取舍规则,只获取结果为True的数据，传入参数为row，mainData的第一行row为1,例如"row%2==1"
}##下级选项为"scaleList" : [], ##存储范围调整，靠后的优先级高,具体配置文件参考scale
detailTitle = {
    "detailTitleName":[], ##明细表标题名
}##下级选项为"scaleList" : [], ##存储范围调整，靠后的优先级高,具体配置文件参考scale
detailData = {
    # "detailDataType": {
    #
    # },
}##下级选项为"scaleList" : [], ##存储范围调整，靠后的优先级高,具体配置文件参考scale
scale = {
    "start" : "默认为当前范围左上角",
    "rows": 0, ##获取指定行数，0表示所有，默认为0
    "columns": 0, ##获取指定列数，0表示所有，默认为0
    "replaceAll" : [ ##整个单元格匹配才替换
        {
            "iniData" : "", ##源数据
            "data" : "", ##目标数据
        }
    ],
    "replaceAll" : [],
    "replaceSome":[ ##包含即替换
        {
            "iniData" : "", ##源数据
            "data" : "", ##目标数据
        }
    ],
    "replaceSome" : [],
    "isDateFormat" : False, ##是否调整日期格式
    "dateFormat" : { #当"isDateFormat"为True时生效
        "targetFormat" : "%Y-%m-%d %H:%M:%S", #目标格式，具体见datetime类格式
        "isEmptyWhenFalse" : True, ##当日期转换失败时，若该项为True，则放置空字符串，若为False，则不改变原值
        "format":[ ##日期格式

        ],
        "dateFormat" :[ ##自定义的日期格式器,写于dateFormat.py中, 传入方法名即可

        ]
    },
    "fillColumns": False, ##是否自动填充空行合并单元格造成的空格, 默认为False
    "fillRows" : False, ##是否自动填充列合并单元格造成的空格, 默认为False
    "setValue" : False, ##设置此区域为某个值
    "setNull" : False, ##设置为空值，此选项具有最高优先级

}

test = excel.copy()
test["sheet"] = sheet.copy()
test["sheet"]["mainTitle"] = mainTitle.copy()
test["sheet"]["mainData"] = mainData.copy()
test["sheet"]["detailTitle"] = detailTitle.copy()
test["sheet"]["datailData"] = detailData.copy()
test["sheet"]["mainTitle"]["scale"] = scale.copy()
test["sheet"]["mainData"]["scale"] = scale.copy()
test["sheet"]["detailTitle"]["scale"] = scale.copy()
test["sheet"]["datailData"]["scale"] = scale.copy()
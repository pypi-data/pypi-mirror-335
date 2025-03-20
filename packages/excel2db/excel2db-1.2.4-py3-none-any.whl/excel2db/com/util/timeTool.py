#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""时间工具
Author: endlessdesert
"""
import datetime, time

def verityFormat(date, format='%Y-%m-%d %H:%M:%S'):
    """
    校验字符串日期格式
    :param date:
    :param format:
    :return:
    >>> verityFormat("2023-07-13 12:00:45", '%Y-%m-%d %H:%M:%S')
    True
    >>> verityFormat("2023-07-13 12:00:", '%Y-%m-%d %H:%M:%S')
    False
    """
    try:
        datetime.datetime.strptime(date, format)
        return True
    except:
        return False

def turnDate(date, Format='default'):
    """
    将输入字符串格式统一
    :param date:
    :param Format:
    :return:
    """
    typ = str(type(date))
    if typ=="<class 'str'>":
        length = len(date)
        if Format=='default':
            if length == 10:
                date = datetime.datetime.strptime(date, '%Y-%m-%d')
            elif length == 19:
                date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            elif length == 26:
                date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
        else:
            date = datetime.datetime.strptime(date, Format)
    else:
        length = 0
    return date,typ,length

##转换为源格式
def backDate(date,typ,length, Format='default'):
    if typ=="<class 'str'>" and Format=='default':
        if length == 10:
            date = date.strftime('%Y-%m-%d')
        elif length == 19:
            date = date.strftime('%Y-%m-%d %H:%M:%S')
        elif length == 26:
            date = date.strftime('%Y-%m-%d %H:%M:%S.%f')
    else:
        date = date.strftime(Format)
    return date

# ##时间比较
# ##输入长时间格式字符串
# def cmp_date(date1, date2, Format1='default', Format2='default'):
#     """若date1时间大于date2返回True，否则返回False
#
#     :param date1:
#     :param date2:
#     :param Format1:
#     :param Format2:
#     :return:
#     """
#     (date1,typ1,length1) = turnDate(date1, Format1)
#     (date2,typ2,length2) = turnDate(date2, Format2)
#
#     return date1 > date2

def cmp_date(date1, date2, Format1='default', Format2='default'):
    """若date1时间大于date2返回1，小于返回-1, 等于返回0
    时间比较
    :param date1:
    :param date2:
    :param Format1:
    :param Format2:
    :return:
    >>> cmp_date("2023-07-13 12:00:45", "2023-07-13 12:00:45")
    0
    >>> cmp_date("2023-07-13 12:00:45", "2023-07-13 12:00:46")
    -1
    >>> cmp_date("2023-07-13 12:00:45", "2023-07-13 12:00:44")
    1
    """
    (date1, typ1, length1) = turnDate(date1, Format1)
    (date2, typ2, length2) = turnDate(date2, Format2)

    if date1 > date2:
        return 1
    elif date1 < date2:
        return -1
    else:
        return 0

def yesterday(date, num = 1, Format='default'):
    """
    返回前num天时间,数量取决于参数num
    :param date:
    :param num:
    :param Format:
    :return:
    >>> yesterday("2023-07-13 12:00:45")
    '2023-07-12 12:00:45'
    >>> yesterday("2023-07-13", num=2)
    '2023-07-11'
    """
    (date,typ,length) = turnDate(date, Format = Format)
    
    date = date - datetime.timedelta(days=num)

    return backDate(date,typ,length)

def nextday(date, num = 1, Format='default'):
    """
    返回后一天时间
    :param date:
    :param num:
    :param Format:
    :return:
    >>> nextday("2023-07-13 12:00:45")
    '2023-07-14 12:00:45'
    >>> nextday("2023-07-13", num=2)
    '2023-07-15'
    """
    (date,typ,length) = turnDate(date, Format = Format)
    
    date = date + datetime.timedelta(days=num)
    
    return backDate(date,typ,length)

##获取当前高精度时间
def getNowLong():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

##获取当前长时间
def getNow(Format='%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.now().strftime(Format)
    
def changeTime(date, unit, num, Format='default'):
    """
    改变时间某个值
    :param date:
    :param unit:
    :param num:
    :param Format:
    :return:
    """
    (date,typ,length) = turnDate(date, Format = Format)
    
    if unit == 'days':
        date = date + datetime.timedelta(days=num)
    elif unit == 'hours':
        date = date + datetime.timedelta(hours=num)
    elif unit == 'minutes':
        date = date + datetime.timedelta(minutes=num)
    elif unit == 'seconds':
        date = date + datetime.timedelta(seconds=num)
    elif unit == 'weeks':
        date = date + datetime.timedelta(weeks=num)
    elif unit == 'milliseconds':
        date = date + datetime.timedelta(milliseconds=num)
        
    return backDate(date,typ,length)
    
##返回时间差
##返回date1减去date2，unit为单位，支持天，时，分，秒
def timeSubtract(date1, date2, unit='d', Format='default'):
    (date1,typ1,length1) = turnDate(date1, Format = Format)
        
    (date2,typ2,length2) = turnDate(date2, Format = Format)
    
    date = date1 - date2
    
    if unit == 'd':
        return date.days
    elif unit == 'H':
        return date.days*24 + date.seconds//3600
    elif unit == 'M':
        return date.days*24*60 + date.seconds//60
    elif unit == 'S':
        return date.days*24*3600 + date.seconds
    elif unit == 'MS': ##毫秒
        return (date.days*24*3600 + date.seconds)*1000000 + date.microseconds
    elif unit == 'LS': ##包含小数的秒
        return date.days*24*3600 + date.seconds + date.microseconds/1000000

##时间转字符串
def dateToStr(date, Format='%Y-%m-%d %H:%M:%S'):
    (date,typ,length) = turnDate(date, Format = Format)
    return date.strftime(Format)
    
##字符串转时间
def strToDate(date, Format="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.strptime(date, Format)
    

def getPart(unit='d', date=getNow(), Format='default'):
    """
    ##返回时间的某个字段的int类型
    ##默认获取当前时间
    :param unit: 支持参数类型
    "Y":年;"m":月;"d":天;"H":小时;"M":分钟;"S":秒
    :param date:
    :return:
    """
    (date,typ,length) = turnDate(date, Format = Format)

    if unit == 'Y':
        return int(date.strftime('%Y'))
    elif unit == 'm':
        return int(date.strftime('%m'))
    elif unit == 'd':
        return int(date.strftime('%d'))
    elif unit == 'H':
        return int(date.strftime('%H'))
    elif unit == 'M':
        return int(date.strftime('%M'))
    elif unit == 'S':
        return int(date.strftime('%S'))
    
##生成当前时间戳
def getTimeStamp():
    return str((int(round(time.time() * 1000))))

def getStartAndEndTime(date=getNow(), unit='d', Format='default'):
    """
    ##返回时间所处范围的开始时间(包含)和结束时间(不包含)
    ##默认根据当前时间
    ##默认获取当天开始与结束时间
    :param unit:支持的参数
    "Y":年;"m":月;"d":天;"H":小时;"M":分钟;"S":秒
    :param date:
    :return:
    >>> getStartAndEndTime("2023-07-23 12:45:56", "Y")
    ('2023-01-01 00:00:00', '2024-01-01 00:00:00')
    >>> getStartAndEndTime("2023-12-23 12:45:56", "m")
    ('2023-12-01 00:00:00', '2024-01-01 00:00:00')
    >>> getStartAndEndTime("2023-07-23 12:45:56", "W")
    ('2023-07-17 00:00:00', '2023-07-23 00:00:00')
    >>> getStartAndEndTime("2023-07-23 12:45:56", "d")
    ('2023-07-23 00:00:00', '2023-07-24 00:00:00')
    """
    (date, typ, length) = turnDate(date, Format=Format)

    if unit == 'Y':
        startTime = datetime.datetime(date.year, 1, 1).strftime('%Y-%m-%d %H:%M:%S')
        endTime = datetime.datetime(date.year+1, 1, 1).strftime('%Y-%m-%d %H:%M:%S')
    elif unit == 'm':
        startTime = datetime.datetime(date.year, date.month, 1).strftime('%Y-%m-%d %H:%M:%S')
        endTime = datetime.datetime(date.year if date.month<12 else date.year+1, date.month + 1 if date.month<12 else 1, 1).strftime('%Y-%m-%d %H:%M:%S')
    elif unit == 'W':
        startTime = (date - datetime.timedelta(days=date.weekday())).strftime('%Y-%m-%d %H:%M:%S')
        endTime = (date + datetime.timedelta(days=6 - date.weekday())).strftime('%Y-%m-%d %H:%M:%S')
        startTime = startTime[:10] + " 00:00:00"
        endTime = endTime[:10] + " 00:00:00"
    elif unit == 'd':
        startTime = date.date().strftime('%Y-%m-%d %H:%M:%S')
        endTime = (date.date() + datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    # elif unit == 'H':
    #     startTime = ""
    #     endTime = ""
    # elif unit == 'M':
    #     startTime = ""
    #     endTime = ""

    return startTime, endTime

if __name__ == "__main__":
    import doctest
    doctest.testmod()
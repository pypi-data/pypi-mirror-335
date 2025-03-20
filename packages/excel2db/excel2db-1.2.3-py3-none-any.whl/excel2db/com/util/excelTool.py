# -*- coding:utf8 -*-
"""
excel工具
"""
import re, string

"""
自适应列宽
"""

def toStr(data):
    """
    数据转字符串
    """
    if data != data:
        return data
    elif isinstance(data, str):
        return data
    else:
        return str(data)

def letterToNumber(code):
    """
    将excel列标字母转换为数字
    输入"AA+45"，输出(45,27)
    输入"45+AA"，输出(45,27)
    输入"AA", 输出27
    输入"45", 输出45
    :return:
    """

    def isLetter(str):
        """
        字符串是否都是字母
        """
        flag = True
        for i in str:
            if i not in string.ascii_letters:
                flag = False
                break
        return flag

    def isDigit(str):
        """
        字符串是否都是数字
        """
        flag = True
        for i in str:
            if i not in string.digits:
                flag = False
                break
        return flag

    def letterToNumber(str):
        """
        字母转数字，相当于26进制
        """
        length = len(str)
        num = 0
        for index, letter in enumerate(str):
            num += 26 ** (length - 1 - index) * (ord(letter) - 64)
        return num

    if not isinstance(code, str):
        return False

    lis = code.split("+")  ##分割为字母和数字

    if len(lis) not in (1, 2):
        return False

    if len(lis) == 1:
        if isDigit(lis[0]):
            return int(lis[0])
        elif isLetter(lis[0]):
            return letterToNumber(lis[0])
        else:
            return False

    else:
        if isDigit(lis[0]) and isLetter(lis[1]):  ##左数字右字母
            return int(lis[0]), letterToNumber(lis[1])
        elif isDigit(lis[1]) and isLetter(lis[0]):
            return int(lis[1]), letterToNumber(lis[0])
        else:
            return False

def numberToLetter(num):
    """
    数字转字母，相当于26进制
    """
    st = ""
    num -= 1
    while (num >= 26):
        out = num // 26
        r = num - out * 26
        st = chr(r + 65) + st
        num = out - 1

    st = chr(num + 65) + st
    return st

def style_excel(sheet, CHINESECHARLENGTH = 2.3, OTHERCHARLENGTH = 1.3):
    """
    自适应列宽
    :param sheet: openpyxl中的sheet
    :param CHINESECHARLENGTH: 中文字符长度
    :param OTHERCHARLENGTH: 其他字符长度
    :return:
    """
    # 获取最大行数与最大列数
    max_column = sheet.max_column
    max_row = sheet.max_row

    # 将每一列，单元格列宽最大的列宽值存到字典里，key:列的序号从1开始(与字典num_str_dic中的key对应)；value:列宽的值
    max_column_dict = {}

    # 遍历全部列
    for i in range(1, max_column + 1):
        # 遍历每一列的全部行
        for j in range(1, max_row + 1):
            column = 0
            # 获取j行i列的值
            sheet_value = sheet.cell(row=j, column=i).value
            column = (CHINESECHARLENGTH - OTHERCHARLENGTH) * len(
                re.findall('([\u4e00-\u9fa5])', str(sheet_value))) + OTHERCHARLENGTH * len(str(sheet_value))

            # 当前单元格列宽与字典中的对比，大于字典中的列宽值则将字典更新。如果字典没有这个key，抛出异常并将值添加到字典中
            try:
                if column > max_column_dict[i]:
                    max_column_dict[i] = column
            except Exception as e:
                max_column_dict[i] = column
    # 此时max_column_dict字典中已存有当前sheet的所有列的最大列宽值，直接遍历字典修改列宽
    for key, value in max_column_dict.items():
        sheet.column_dimensions[numberToLetter(key)].width = value

if __name__ == '__main__':
    v= '时'
    print(v.isdigit())


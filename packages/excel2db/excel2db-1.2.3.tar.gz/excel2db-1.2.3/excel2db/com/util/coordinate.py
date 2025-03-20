# -*- coding:utf8 -*-

class coordinate:
    def __init__(self, position):
        """
        二维整数集合运算
        :param position:
        """
        self.position = position.copy() if isinstance(position,list) else list(position)  ##四边定位信息
        self.rows = position[1] - position[0] + 1  ##行数
        self.columns = position[3] - position[2] + 1  ##列数
        self.start = (position[0], position[2])  ##左上角坐标
        if self.rows >= 1 and self.columns >= 1:
            self.STATUS = 0 ##若表不存在时，则状态为1
            temp = [1 for i in range(self.columns)]
            self.numSet = [temp.copy() for i in range(self.rows)]  ##信息表
        else:
            self.STATUS = 1

    def copy(self):
        temp = coordinate(self.position.copy())
        temp.numSet = self.numSet.copy()
        return temp

    def getAllCoordinate(self):
        coordinateSet = []
        for i in range(self.rows):
            for j in range(self.columns):
                if self.numSet[i][j]:
                    coordinateSet.append((self.start[0] + i, self.start[1] + j))
        return coordinateSet

    def isCell(self, x, y):
        """
        判断某个坐标是否有值
        :param x:
        :param y:
        :return:
        """
        return self.numSet[x - self.start[0]][y - self.start[1]]

    def setCell(self, x, y, value):
        """
        设置某个坐标的值
        :param x:
        :param y:
        :return:
        """
        self.numSet[x - self.start[0]][y - self.start[1]] = value

    def __add__(self, other):
        """
        重载加运算，作为交集
        :param other:
        :return:若无交集返回None
        """
        ##判断是否具有交集
        def lineCover(line1:list, line2:list):
            """
            判断两闭区间是否重叠
            :param line1: 闭区间1
            :param line2: 闭区间2
            :return:若重叠，返回重叠闭区间，否则返回None
            """
            if line1[0] < line2[0]:
                if line1[1] >= line2[0]:
                    if line1[1] >= line2[1]:
                        return line2[0], line2[1]
                    else:
                        return line2[0], line1[1]
                else:
                    return None
            elif line1[0] == line2[0]:
                if line1[1] >= line2[1]:
                    return line1[0], line2[1]
                else:
                    return line1[0], line1[1]
            else:
                if line2[1] >= line1[0]:
                    if line1[1] >= line2[1]:
                        return line1[0], line2[1]
                    else:
                        return line1[0], line1[1]
                else:
                    return None

        rowCoordinate = lineCover(self.position[:2], other.position[:2])
        columnCoordinate = lineCover(self.position[2:], other.position[2:])
        if rowCoordinate == None or columnCoordinate == None: ##若无交集
            binSet = coordinate([1,1,1,1])
            binSet.STATUS = 1

            return binSet

        binSetPosition = rowCoordinate + columnCoordinate  ##并集的四边定位
        binSet = coordinate(binSetPosition)  ##定义交集区域
        ##检测该区域是否属于交集
        for i in range(binSet.rows):
            for j in range(binSet.columns):
                x, y = i + binSet.start[0], j + binSet.start[1]
                if self.isCell(x, y) and other.isCell(x, y):
                    pass
                else:
                    binSet.numSet[i, j] = 0

        if binSet.isEmpty(): ##若交集为空
            binSet.STATUS = 1

        return binSet

    def __sub__(self, other):
        """
        重载减运算
        :param other:
        :return:
        """
        subSet = self.copy()
        binSet = self + other

        if binSet.STATUS:
            return subSet

        for i in range(binSet.rows):  ##去除并集中的内容
            for j in range(binSet.columns):
                x, y = i + binSet.start[0], j + binSet.start[1]
                if subSet.isCell(x, y):
                    subSet.setCell(x, y, 0)

        subSet.removeExcess()
        return subSet

    def isEmpty(self):
        """
        判断是否有元素
        :return: 没有返回False
        """
        for row in self.numSet:
            for value in row:
                if value:
                    return False
        return True

    def removeExcess(self):
        """
        缩小不必要的范围
        """
        ##缩小上行
        if self.isEmpty():
            self.STATUS = 1
            return

        numTemp = 0
        for i in range(self.rows):  ##去除并集中的内容
            flag = 1
            for j in range(self.columns):
                if self.numSet[i][j]:  ##若存在元素
                    flag = 0
                    break

            if flag:
                numTemp += 1
            else:
                break

        if numTemp:  ##缩小处理
            self.position[0] += numTemp
            self.rows = self.position[1] - self.position[0] + 1  ##行数
            self.columns = self.position[3] - self.position[2] + 1  ##列数
            self.start = (self.position[0], self.position[2])  ##左上角坐标
            self.numSet = self.numSet[numTemp:]

        ##缩小下行
        numTemp = 0
        for i in range(self.rows):  ##去除并集中的内容
            flag = 1
            for j in range(self.columns):
                if self.numSet[self.rows - 1 - i][j]:  ##若存在元素
                    flag = 0
                    break

            if flag:
                numTemp += 1
            else:
                break

        if numTemp:  ##缩小处理
            self.position[1] -= numTemp
            self.rows = self.position[1] - self.position[0] + 1  ##行数
            self.columns = self.position[3] - self.position[2] + 1  ##列数
            self.start = (self.position[0], self.position[2])  ##左上角坐标
            self.numSet = self.numSet[:-numTemp]

        ##缩小左列
        numTemp = 0
        for i in range(self.columns):  ##去除并集中的内容
            flag = 1
            for j in range(self.rows):
                if self.numSet[j][i]:  ##若存在元素
                    flag = 0
                    break

            if flag:
                numTemp += 1
            else:
                break

        if numTemp:  ##缩小处理
            self.position[2] += numTemp
            self.rows = self.position[1] - self.position[0] + 1  ##行数
            self.columns = self.position[3] - self.position[2] + 1  ##列数
            self.start = (self.position[0], self.position[2])  ##左上角坐标
            for index, values in enumerate(self.numSet):
                self.numSet[index] = self.numSet[index][numTemp:]

        ##缩小右列
        numTemp = 0
        for i in range(self.columns):  ##去除并集中的内容
            flag = 1
            for j in range(self.rows):
                if self.numSet[j][self.columns - 1 - i]:  ##若存在元素
                    flag = 0
                    break

            if flag:
                numTemp += 1
            else:
                break

        if numTemp:  ##缩小处理
            self.position[3] -= numTemp
            self.rows = self.position[1] - self.position[0] + 1  ##行数
            self.columns = self.position[3] - self.position[2] + 1  ##列数
            self.start = (self.position[0], self.position[2])  ##左上角坐标
            for index, values in enumerate(self.numSet):
                self.numSet[index] = self.numSet[index][:-numTemp]
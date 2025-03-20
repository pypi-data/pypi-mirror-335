# -*- coding: utf-8 -*-

import base64, os, shutil, random

##文件操作工具类
class fileTool(object):
    
    def __init__(self):
        pass
    
    ##检查文件是否存在
    def fileIsExists(self, url):
        if os.path.exists(url):
            return os.path.isfile(url)
        else: 
            return False
        
    ##检查目录是否存在
    def dirIsExists(self, url):
        if os.path.exists(url):
            return os.path.isfile(url) == False
        else: 
            return False

    ##创建目录
    def createDir(self, dirUrl, mode=0):
        """
        创建文件夹
        :param dirUrl: 文件夹路径
        :param mode:
        0：重名，则在后面添加随机数，并返回完整路径名
        1：覆盖，返回完整路径名
        2：不覆盖，重名返回False，不重名返回完整路径名
        :return:
        """
        try:
            if os.path.exists(dirUrl):  ##若存在同名路径
                if mode == 0:
                    index = 0
                    outDirUrl = dirUrl + str(index)
                    while (os.path.exists(outDirUrl)):
                        index += 1
                        outDirUrl = dirUrl + str(index)
                    os.mkdir(outDirUrl)
                    return outDirUrl

                elif mode == 1:
                    if self.fileIsExists(dirUrl):
                        os.remove(dirUrl)
                    else:
                        shutil.rmtree(dirUrl)
                    os.mkdir(dirUrl)
                    return dirUrl

                elif mode == 2:
                    return False

                else:
                    return False
            else:
                os.mkdir(dirUrl)
                return dirUrl
        except FileNotFoundError:
            return False


    def writeOverFile(self,url,info, typ='str', code='utf8'):
        """
        覆盖写文件
        :param url: 文件路径
        :param info: 写入信息
        :param typ: 类型为str还是二进制
        :param code: 编码默认为utf8
        :return:
        """
        a=open(url, 'wb')##a为追加，r为只读，w为覆盖写
        if typ=='str':
            a.write(bytes(info, encoding = code))
        else:
            a.write(info)
        a.flush()
        a.close()
        
    ##追加写文件
    def writeConFile(self,url,info, typ='str', code='utf8'):
        a=open(url, 'ab')##a为追加，r为只读，w为覆盖写
        if typ=='str':
            a.write(bytes(info, encoding = code))
        else:
            a.write(info)
        a.flush()
        a.close()
        
    ##一次性读取文件
    def readAllFile(self,url, typ='str', code='utf8'):
        a=open(url, 'rb')##a为追加，r为只读，w为覆盖写
        info = a.read()
        if typ=='str':
            info = str(info, code)
        a.close()
        return info
    
    ##复制文件
    def copyFile(self, url, newurl):
        info = self.readAllFile(url, typ='b')
        self.writeOverFile(newurl, info, typ='b')
        
        # shutil.copy(url, newurl)
    
    ##获取文件大小
    ##url 文件路径
    ##unit 单位，默认为kb
    def getSize(self, url, unit='kb'):
        size = os.path.getsize(url)
        unit = unit.lower()
        if unit == 'b':
            return size
        elif unit == 'kb':
            return size/1024
        elif unit == 'mb':
            return size/1024/1024
        elif unit == 'gb':
            return size/1024/1024/1024
        elif unit == 'tb':
            return size/1024/1024/1024/1024
        elif unit == 'pb':
            return size/1024/1024/1024/1024/1024
    
    ##输入文件路径
    ##输出base64字符串
    def fileToBase64(self, url, typ='str', code='utf8'):
        a = open(url, 'rb')
        data = a.read()
        base64_data = base64.b64encode(data)
        if typ=='str':
            base64_data = str(base64_data,code)
        return base64_data
    
    ##输入文件路径和base64字符串
    ##输出解码后的文件到文件路径
    def base64ToFile(self, url,ba64, typ = 'str', code='utf8'):
        a=open(url, 'wb')##a为追加，r为只读，w为覆盖写
        if typ == 'str':
            ba64 = bytes(ba64, encoding = code)
        ba64 = base64.b64decode(ba64)
        a.write(ba64)
        a.flush()
        a.close()
        
    ##删除文件
    def deleteFile(self, url):
        os.remove(url)
        
    ##获取路径filepath下所有类型为typ的文件
    def getFileNameByType(self,filePath,typ=[]):
        lis = []
        typTemp = typ.copy()
        for i in typTemp:
            if i[0] == '.':
                typ.append(i[1:])
            else:
                typ.append('.' + i)
        
        for i in os.listdir(filePath):
            suffix = os.path.splitext(i)[1]
            if suffix in typ:
                lis.append(i)
        return lis

    ##创建新文件
    def createNewFile(self, areadyList, typ, length):
        """
        创建新文件名
        :param areadyList: 已存在文件列表
        :param typ: 文件类型或相同类型的文件名(例如.jpg或wf.jpg)
        :param length: 文件名长度(不包含类型)
        :return: 返回文件名
        """
        if isinstance(typ, str):
            if len(typ) > 0:
                if typ[0] != '.':
                    typ = '.' + os.path.splitext(typ)[1]

        charactersStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        while True:
            newFileName = ''.join(random.sample(charactersStr, length)) + typ
            if newFileName not in areadyList:
                return newFileName
    
    ##分割文件名和文件类型
    ##(name, suffix) = os.path.splitext(infile)
    
    ##分割文件路径和文件名
    ##(path, fileName) = os.path.split(url)
    
    ##返回路径filepath下所有的文件夹和文件名称
    ##os.listdir(filePath)
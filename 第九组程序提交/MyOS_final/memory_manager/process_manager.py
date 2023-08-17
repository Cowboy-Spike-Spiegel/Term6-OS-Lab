import math


# 每个进程的单独管理,包括页表,使用的内存量等
class ProcessManager:
    def __init__(self, defaultLru=8, pageSize=16, lrupper=12):
        self.maxAddress = -1
        self.pageSize = pageSize
        # [-1, -1, 0, 0] -> [虚存页号， 物理内存页号， 有效位， 是否在物理内存中被修改], 数组下标为页号
        self.table = []
        self.lru = []
        self.maxLru = defaultLru
        self.lostPage = 0
        self.accessTimes = 0
        self.lrupper = lrupper
        # {文件名: [首地址, 大小, 块号, 是否代码段]}
        self.file = {}

    # 增加页表项,配合内存的申请
    def add(self, ret):
        for i in ret:
            self.table.append([i, -1, 0, 0])
            self.maxAddress += self.pageSize

    # 检查访问/写入地址是否合法
    def ifPolicy(self, address, length):
        if address < 0 or address + length - 1 > self.maxAddress:
            return -1
        return 0

    # 释放页表
    def free(self, address, length):
        ret = self.findAllPage(address, length)
        result = []
        flag = 0
        for i in ret:
            result.append([self.table[i - flag][0], self.table[i - flag][1]])
            self.table.pop(i - flag)
            if i in self.lru:
                self.lru.remove(i)
            flag += 1
        return result

    # 根据地址和长度找出所有需要访问的虚拟页
    def findAllPage(self, address, length):
        return [i + address // self.pageSize for i in
                range(0, math.ceil((length + address % self.pageSize) / self.pageSize))]

    # 找出所访问内容是否在物理内存中,如果在返回物理页号，否则返回虚拟页号
    def ifInPhyMem(self, address, length):
        ret = self.findAllPage(address, length)
        result = []
        for i in ret:
            if self.table[i][2] == 1:
                result.append([1, self.table[i][1]])
            else:
                result.append([0, i])
        return result

    # 传入虚拟页，换页，传回参数给管理模块调度
    def swaPage(self, page):

        self.ifAddLru()

        # 访存次数加一
        self.accessTimes += 1

        if page in self.lru and self.table[page][2] == 1:
            self.lru.remove(page)
            self.lru.append(page)
            return [1, self.table[page][1]]

        # 用于计算缺页率
        self.lostPage += 1

        if len(self.lru) < self.maxLru:
            self.lru.append(page)
            return [0, [[-1], [page, self.table[page][0]]]]
        else:
            lost = self.lru.pop(0)
            self.lru.append(page)
            return [0, [[lost, self.table[lost][1], self.table[lost][3], self.table[lost][0]],
                        [page, self.table[page][0]]]]

    # 字如其名
    def modify(self, page, flag, value):
        self.table[page][flag] = value

    # 动态分配,缺页率过高时增加lru表
    def ifAddLru(self, step=10, threshold=0.4):
        # 访存次数过少，没有参考意义
        if self.accessTimes < step * self.maxLru:
            return
        # 无需每次访存都判断，step次访存判断一次
        if self.accessTimes % step != 0:
            return
        if self.lostPage / self.accessTimes > threshold and self.maxLru < self.lrupper:
            self.maxLru += 1

    # 记录存入了哪些文件
    def addFile(self, name, address, size, block, flag):
        self.file[name] = [address, size, block, flag]

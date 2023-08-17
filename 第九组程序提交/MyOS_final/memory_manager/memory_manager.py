import copy

from .draw_grap import drawGrap
from .memory import Memory
from .process_manager import ProcessManager
from .string_operation import cutString


# 总管理模块
class MemoryManager:
    def __init__(self, pageSize=16, pageNum=128, step=2, orderLen=4):
        self.virMem = Memory(pageSize, pageNum * step)
        self.phyMem = Memory(pageSize, pageNum)
        self.step = step
        self.processTable = {}
        self.pageNum = pageNum
        self.pageSize = pageSize
        self.orderLen = orderLen
        self.path = -2
        self.dataa = -3

    # 从address开始访问长度为Length的内存
    def access(self, pid, address, length):
        manager = self.processTable.get(pid)
        if manager is None:
            return -1
        if manager.ifPolicy(address, length) == -1:
            return -1
        ret = manager.findAllPage(address, length)
        accessPage = []
        j = 0
        data = []
        offset = address % self.pageSize
        for k in ret:
            i = manager.swaPage(k)

            if i[0] == 1:
                accessPage.append(i[1])
            else:
                if i[1][0][0] != -1:
                    if i[1][0][2] == 1:
                        self.virMem.copy(i[1][0][3], self.phyMem.memory[i[1][0][1]])
                    self.phyMem.free([i[1][0][1]])
                    manager.modify(i[1][0][0], 2, 0)
                num = self.phyMem.malloc(self.pageSize)
                if num != -1:
                    manager.modify(i[1][1][0], 1, num[0])
                    manager.modify(i[1][1][0], 2, 1)
                    self.phyMem.copy(num[0], self.virMem.memory[i[1][1][1]])
                accessPage.append(num[0])

            if len(ret) == 1:
                data.append(self.phyMem.access(accessPage[j] * self.pageSize + offset, length))
            elif j == len(ret) - 1:
                data.append(self.phyMem.access(accessPage[j] * self.pageSize,
                                               length + offset - (len(ret) - 1) * self.pageSize))
            elif j == 0:
                data.append(self.phyMem.access(offset + accessPage[j] * self.pageSize, self.pageSize - offset))

            else:
                data.append(self.phyMem.access(accessPage[j] * self.pageSize, self.pageSize))
            j += 1

        print("pid =", pid, ", address =", address, ", len =", length, "\n访问的物理页:", accessPage)
        print("LRU =", manager.lru, "\ncontent:")
        return "".join(data)

    # 申请 size 大小内存
    def malloc(self, pid, size):
        if self.processTable.get(pid) is None:
            self.processTable[pid] = ProcessManager()
        ret = self.virMem.malloc(size)
        if ret != -1:
            self.processTable[pid].add(ret)
            return
        else:
            return -1

    # 从address开始释放长度为length的内存
    def free(self, pid, address, length):
        if self.processTable.get(pid) is None:
            return -1
        if self.processTable.get(pid).ifPolicy(address, length) == -1:
            return -1
        ret = self.processTable.get(pid).free(address, length)
        vir = []
        phy = []
        for i in ret:
            if i[0] != -1:
                vir.append(i[0])
            if i[1] != -1:
                phy.append(i[1])
        self.virMem.free(vir)
        self.phyMem.free(phy)

    # 从address开始写入length, 内容为string
    def write(self, pid, address, length, string):
        manager = self.processTable.get(pid)
        if manager is None:
            return -1
        if manager.ifPolicy(address, length) == -1:
            return -1
        ret = manager.findAllPage(address, length)

        offset = address % self.pageSize
        proprotion = []
        for i in range(len(ret)):
            if i == 0:
                proprotion.append(self.pageSize - offset)
            elif i == len(ret) - 1:
                proprotion.append(length + offset - (len(ret) - 1) * self.pageSize)
            else:
                proprotion.append(self.pageSize)
        strings = cutString(proprotion, string)

        accessPage = []
        j = 0
        for k in ret:

            i = manager.swaPage(k)

            if i[0] == 1:
                accessPage.append(i[1])
            else:
                if i[1][0][0] != -1:
                    if i[1][0][2] == 1:
                        self.virMem.copy(i[1][0][3], self.phyMem.memory[i[1][0][1]])
                    self.phyMem.free([i[1][0][1]])
                    manager.modify(i[1][0][0], 2, 0)
                num = self.phyMem.malloc(self.pageSize)
                if num != -1:
                    manager.modify(i[1][1][0], 1, num[0])
                    manager.modify(i[1][1][0], 2, 1)
                    self.phyMem.copy(num[0], self.virMem.memory[i[1][1][1]])
                accessPage.append(num[0])
            if len(ret) == 1:
                self.phyMem.write(offset + accessPage[j] * self.pageSize, length, strings[j])
            elif j == 0:
                self.phyMem.write(offset + accessPage[j] * self.pageSize, self.pageSize - offset, strings[j])
            elif j == len(ret) - 1:
                self.phyMem.write(accessPage[j] * self.pageSize,
                                  length + offset - (len(ret) - 1) * self.pageSize, strings[j])
            else:
                self.phyMem.write(accessPage[j] * self.pageSize, self.pageSize, strings[j])
            j += 1
            manager.modify(k, 3, 1)
        print("pid =", pid, ", address =", address, ", len =", length, "\n写入的物理页:", accessPage)
        print("LRU =", manager.lru, "\n")

    # 释放该进程所有内存
    def freeAllMem(self, pid):
        manager = self.processTable.get(pid)
        if manager is None:
            return -1
        self.free(pid, 0, manager.maxAddress)
        self.processTable.pop(pid)

    # 外部接口
    def alloc(self, path, pid, window):

        # 使用路径从磁盘获取
        window.signals.get_path.emit(path)
        while self.path == -2:
            continue

        data = self.path
        self.path = -2

        if data == -1 or data is None or data[0] == "":
            return -1

        strings = data[0].split("\n")
        if self.malloc(pid, len(strings) * self.orderLen) != -1:
            self.processTable.get(pid).addFile(path, 0, len(strings) * self.orderLen, data[2], 1)
            pc = 0
            for i in strings:
                self.write(pid, pc * self.orderLen, self.orderLen, i)
                pc += 1
            return len(strings) * self.orderLen
        else:
            return -1

    def alloc_fork(self, fpid, cpid):
        fmanager = self.processTable.get(fpid)
        if fmanager is None:
            return -1
        if self.malloc(cpid, fmanager.maxAddress + 1) == -1:
            return -1
        cmanager = self.processTable.get(cpid)
        cmanager.file = copy.deepcopy(fmanager.file)
        for value in fmanager.file.items():
            if value[1][3] == 1:
                num = value[1][1] // self.orderLen
                for i in range(num):
                    self.write(cpid, i * self.orderLen, self.orderLen,
                               self.access(fpid, i * self.orderLen, self.orderLen))
            else:
                self.write(cpid, value[1][0], value[1][1], self.access(fpid, value[1][0], value[1][1]))
        return 1

    def read_file(self, pid, path, data, win=None):
        if win is not None:
            win.signals.get_path.emit(path)
            while self.path == -2:
                continue

            data = self.path
            self.path = -2



        if pid == -1 and self.processTable.get(-1) is None:
            self.malloc(-1, data[1])




        # return [文件内容, size, block]
        if data is None:
            return
        if data == -1:
            return data
        if data[0] == '':
            manager = self.processTable.get(pid)
            if manager.file.get(path) is not None:
                manager.file.pop(path)
            return -1
        manager = self.processTable.get(pid)
        preMax = manager.maxAddress
        if manager.file.get(path) is None:
            if self.malloc(pid, data[1]) == -1:
                return -1
            self.write(pid, preMax + 1, data[1], data[0])
            manager.addFile(path, preMax + 1, data[1], data[2], 0)
            return data[0]
        else:
            preFile = manager.file.get(path)
            preFileData = self.access(pid, preFile[0], preFile[1])
            if data[0] == preFileData:
                return data[0]
            else:
                if preMax - preFile[0] + 1 < data[1]:
                    if self.malloc(pid, data[1] - 1 - preMax + preFile[0]) == -1:
                        return -1
                self.write(pid, preFile[0], data[1], data[0])
                manager.addFile(path, preFile[0], data[1], data[2], 0)
                return data[0]

    def out_file(self, pid, path):

        manager = self.processTable.get(pid)
        if manager is None:
            return -1
        data = manager.file.get(path)
        if data is None:
            self.freeAllMem(-1)
            return -1
        string = []
        if data[3] == 1:

            num = data[1] // self.orderLen
            for i in range(0, num):
                string.append(self.access(pid, data[0] + i * self.orderLen, self.orderLen))
            string = "\n".join(string)
        else:
            string = self.access(pid, data[0], data[1])
        if pid == -1:
            manager.file.pop(path)
            self.freeAllMem(-1)
        return [path, string]

    def draw_memory(self, type):
        data = [[self.pageNum, self.pageNum * self.step]]
        for pid, manager in self.processTable.items():
            virNum = 0
            phyNum = 0
            for j in manager.table:
                virNum += 1
                if j[2] == 1:
                    phyNum += 1
            data.append([pid, virNum, phyNum])
        return drawGrap(data, type)
# end

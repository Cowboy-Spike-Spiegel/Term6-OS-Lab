import copy
import math

from .page import Page


class Memory:
    def __init__(self, pageSize=16, pageNum=128):
        self.maxPage = pageNum
        self.pageSize = pageSize
        # record used memory, kb
        self.used = 0
        self.maxMem = pageSize * pageNum
        # [how many use:<= pageSize]
        self.memory = [Page(pageSize) for i in range(self.maxPage)]

    def access(self, address, length):
        page = address // self.pageSize
        if page >= self.maxPage or length > self.pageSize:
            return -1
        offset = address % self.pageSize
        if offset + length > self.pageSize:
            return -1
        return self.memory[page].access(offset, length)

    def malloc(self, size):
        if size == 0:
            size = self.pageSize
        if self.used + size > self.maxMem:
            return -1
        ret = []
        num = math.ceil(size / self.pageSize)
        for i in range(len(self.memory)):
            if self.memory[i].used == 0:
                self.memory[i].used = 1
                self.used += self.pageSize
                ret.append(i)
                num -= 1
            if num == 0:
                return ret

    def free(self, ret):
        for i in ret:
            self.memory[i] = Page(self.pageSize)

    def copy(self, num, page):
        self.memory[num] = copy.deepcopy(page)

    def write(self, address, length, string):
        page = address // self.pageSize
        if page >= self.maxPage or length > self.pageSize:
            return -1
        offset = address % self.pageSize
        if offset + length > self.pageSize:
            return -1
        self.memory[page].write(offset, length, string)
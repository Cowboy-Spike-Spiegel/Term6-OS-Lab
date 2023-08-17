from .data import Data
from .string_operation import cutString


class Page:
    def __init__(self, pageSize=16):
        self.maxSize = pageSize
        # if have used
        self.used = 0
        # [[(Start, End)], 标志哪些部分的地址被使用
        self.usedAddress = [(pageSize + 1, pageSize + 2)]
        # 键为数据首地址， 值为数据
        self.content = {}

    # 业内访问,从偏移量开始访问length,返回字符串
    def access(self, offset, length):
        # 越界
        if offset + length > self.maxSize or offset < 0:
            return -1
        if length == 0:
            return -1

        self.usedAddress.sort(key=lambda x: x[0])
        start = offset
        end = offset + length
        sflag = -1
        eflag = -1
        for i in range(len(self.usedAddress)):
            if self.usedAddress[i][0] <= start <= self.usedAddress[i][1]:
                sflag = i

            if self.usedAddress[i][0] <= end <= self.usedAddress[i][1]:
                eflag = i

        data = []
        endData = ""
        startData = ""
        if sflag != -1 and sflag == eflag:
            return self.content.get(self.usedAddress[sflag][0]).access(offset - self.usedAddress[sflag][0], length)
        if sflag != -1:
            startData = self.content.get(self.usedAddress[sflag][0]).access(offset - self.usedAddress[sflag][0],
                                                                            self.usedAddress[sflag][1] - offset + 1)
            start = self.usedAddress[sflag][1]
        if eflag != -1:
            endData = self.content.get(self.usedAddress[eflag][0]).access(0, end - self.usedAddress[eflag][
                0])
            end = self.usedAddress[eflag][0] - 1
        begin = -1
        last = -1
        for i in range(len(self.usedAddress)):
            if self.usedAddress[i][0] > start and begin == -1:
                begin = i
            if self.usedAddress[i][0] > end and last == -1:
                last = i
        if begin != -1 and last != -1:
            for i in range(begin, last):
                data.append(self.content.get(self.usedAddress[i][0]).access(0, self.usedAddress[i][1] -
                                                                            self.usedAddress[i][0] + 1))

        return startData + "".join(data) + endData

    # 从offset开始写入Length,内容为string
    def write(self, offset, length, string):

        if offset + length > self.maxSize or offset < 0:
            return -1
        if length == 0:
            return -1

        self.usedAddress.sort(key=lambda x: x[0])
        start = offset
        end = offset + length
        sflag = -1
        eflag = -1
        for i in range(len(self.usedAddress)):
            if self.usedAddress[i][0] <= start <= self.usedAddress[i][1]:
                sflag = i
            if self.usedAddress[i][0] <= end <= self.usedAddress[i][1]:
                eflag = i

        if sflag != -1 and sflag == eflag:
            start1 = self.usedAddress[sflag][0]
            end1 = self.usedAddress[sflag][1]
            strings1 = cutString([offset - start1, length, end1 - length - offset + 1], self.content.get(start1).string)
            self.free(self.usedAddress[sflag])
            self.writeOne(start1, offset - start1, strings1[0])
            self.writeOne(offset + length, end1 - length - offset + 1, strings1[2])
        else:
            start1 = self.usedAddress[sflag][0]
            end1 = self.usedAddress[sflag][1]
            start2 = self.usedAddress[eflag][0]
            end2 = self.usedAddress[eflag][1]
            if sflag != -1:
                strings2 = cutString([offset - start1, end1 - offset + 1], self.content.get(start1).string)

                self.free((start1, end1))
                self.writeOne(start1, offset - start1, strings2[0])
            if eflag != -1:
                strings3 = cutString([offset + length - start2, end2 - offset - length + 1],
                                     self.content.get(start2).string)
                self.free((start2, end2))
                self.writeOne(offset + length, end2 - offset - length + 1, strings3[1])

        self.usedAddress.sort(key=lambda x: x[0])

        remove = []
        for i in self.usedAddress:
            if i[0] >= offset and i[1] <= end - 1:
                remove.append(i)
        for i in remove:
            self.free(i)
        self.writeOne(offset, length, string)

    def writeOne(self, offset, length, string):

        self.usedAddress.append((offset, offset + length - 1))
        self.content[offset] = Data(string, length)

    def free(self, ret):
        self.usedAddress.remove(ret)
        self.content.pop(ret[0])

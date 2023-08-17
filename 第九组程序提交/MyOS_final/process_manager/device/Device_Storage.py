from .IO_Message import MessageUnit


# 信息存储器
class MsgStorage:
    def __init__(self, capacity):
        self.list = [MessageUnit() for _ in range(capacity)]
        self.capacity = capacity
        self.size = 0

    def clear(self):
        self.list.clear()
        self.list = [MessageUnit() for _ in range(self.capacity)]
        self.size = 0

    # 添加
    def add(self, item: MessageUnit):
        # 满了，不能添加
        if self.size == self.capacity:
            return False
        self.list[self.size] = item
        self.size = self.size + 1
        #print("MsgStorage - added: type =", item.type, ", number =", item.number, ", information =", item.information, ", clock =", item.clock)
        return True

    # 删除
    def remove(self, number):
        for index in range(self.size):
            if self.list[index].number == number:
                item = self.list[index]
                #print("MsgStorage - removed: type =", item.type, ", number =", item.number, ", information =", item.information, ", clock =", item.clock)
                # 因为不是最后一个，所以需要把最后的的搬到这里
                if index < self.size:
                    self.list[index] = self.list[self.size-1]
                self.size = self.size - 1
                return True
        return False

    # 根据index获取信息
    def msg_byIndex(self, index):
        if index < self.size:
            return self.list[index]
        return False

    # 根据index修改时钟数
    def minusClock_byIndex(self, index):
        if index < self.size:
            self.list[index].clock = self.list[index].clock-1
            return True
        return False

    # 根据index修改时钟数
    def addTime_byIndex(self, index):
        if index < self.size:
            self.list[index].time = self.list[index].time + 1
            return True
        return False

    # 根据index修改时钟数
    def convertState_byIndex(self, index, state):
        if index < self.size:
            self.list[index].state = state
            return True
        return False
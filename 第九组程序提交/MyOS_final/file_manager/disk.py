import numpy as np
from .file import *


class Block:

    def __init__(self, block_size):
        self.block_size = block_size  # 块内的大小
        # 文件项
        self.file = File()
        self.file.empty_file()

    # 只能放入一个file
    def store_file(self, file):
        self.file = file

    def rm_file(self):
        self.file = File()
        self.file.empty_file()


class Disk:

    def __init__(self, track_number, sec_number, block_size):
        self.track_number = track_number  # 磁道数
        self.sec_number = sec_number  # 扇区数
        self.block_number = track_number * sec_number  # 磁盘块的总数
        self.block_size = block_size  # 数据块大小

        self.block_free_number = self.block_number  # 初始空闲块数量等于磁盘块总数
        self.free_map = np.zeros([track_number, sec_number], int)

        self.blocks = [[Block(block_size) for i in range(0, self.sec_number)] for i in range(0, self.track_number)]
        self.init_block()

    def reset_map(self,loc):
        """将指定位置的freemap置零

        :param loc: 指定位置
        """
        row = int(loc / self.sec_number)
        col = int(loc % self.sec_number)
        self.free_map[row][col]=0

    # 将块号转换成block对应的位置

    def loc_to_block(self, loc):
        row = int(loc / self.sec_number)
        col = int(loc % self.sec_number)

        return self.blocks[row][col]

    # 分配一个空块
    def alloc_block(self):
        for i in range(0, self.track_number):
            for j in range(0, self.sec_number):
                if self.free_map[i][j] == 0:
                    self.free_map[i][j] = 1
                    loc = i * self.sec_number + j
                    return self.blocks[i][j], loc
        print('无空间可用')

    def init_block(self):
        with open('block.txt') as f:
            for i in range(0, self.track_number):
                for j in range(0, self.sec_number):
                    temp_data = f.readline()
                    temp_data = temp_data.rstrip()
                    self.blocks[i][j].file.name = temp_data
                    temp_data = f.readline()
                    temp_data = temp_data.rstrip()
                    self.blocks[i][j].file.prmis = temp_data
                    temp_data = f.readline()
                    temp_data = temp_data.rstrip()
                    self.blocks[i][j].file.type = temp_data
                    temp_data = f.readline()
                    temp_data = temp_data.rstrip()
                    self.blocks[i][j].file.size = int(temp_data)
                    temp_data = f.readline()
                    temp_data = temp_data.rstrip()
                    self.blocks[i][j].file.ctime = temp_data
                    temp_data = f.readline()
                    temp_data = temp_data.rstrip()
                    self.blocks[i][j].file.mtime = temp_data
                    temp_data = f.readline()
                    temp_data = temp_data.rstrip()
                    if temp_data != '':
                        temp_list = temp_data.split(' ')
                    else:
                        temp_list = list()
                    if len(temp_list) == 0:
                        self.blocks[i][j].file.loc = list()
                    else:
                        for item in temp_list:
                            self.blocks[i][j].file.loc.append(int(item))
                    temp_data = f.readline()
                    temp_content = ''
                    while temp_data != '$\n':
                        temp_content = temp_content + temp_data
                        temp_data = f.readline()
                    temp_content = temp_content.rstrip()
                    self.blocks[i][j].file.content = temp_content
            for i in range(0, self.track_number):
                temp_data = f.readline()
                temp_data = temp_data.rstrip()
                temp_list = temp_data.split(' ')
                for j in range(0, self.sec_number):
                    self.free_map[i][j] = int(temp_list[j])

    def write_block(self):
        with open('block.txt', 'w') as f:
            for i in range(0, self.track_number):
                for j in range(0, self.sec_number):
                    f.write(self.blocks[i][j].file.name)
                    f.write('\n')
                    f.write(self.blocks[i][j].file.prmis)
                    f.write('\n')
                    f.write(self.blocks[i][j].file.type)
                    f.write('\n')
                    f.write(str(self.blocks[i][j].file.size))
                    f.write('\n')
                    f.write(self.blocks[i][j].file.ctime)
                    f.write('\n')
                    f.write(self.blocks[i][j].file.mtime)
                    f.write('\n')
                    for item in self.blocks[i][j].file.loc:
                        f.write(str(item))
                        f.write(' ')
                    f.write('\n')
                    f.write(self.blocks[i][j].file.content)
                    f.write('\n')
                    f.write('$\n')
            for i in range(0, self.track_number):
                for j in range(0, self.sec_number):
                    f.write(str(self.free_map[i][j]))
                    f.write(' ')
                f.write('\n')
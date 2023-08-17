import time


class File:
    def __init__(self, name='', prmis='rwe'):
        self.name = name  # 文件的名字
        self.size = 0  # 文件的大小
        self.prmis = prmis  # 文件的权限
        self.type = ''  # 文件类型
        self.ctime = ''  # 文件创建时间
        self.mtime = ''  # 文件的修改时间
        self.content = ''  # 文件内容
        self.loc = []  # 记录文件占用块数

    # 展示文件基本信息
    def show_basic_msg(self):

        if self.name[0] == '\\':
            print(self.name[1:], end=' ')
        else:
            print(self.name, end=' ')
        print(self.type, end=' ')
        print(self.prmis, end=' ')
        print(self.ctime, end=' ')
        print(self.mtime)

    # 填补时间和文件类型
    def get_type_time(self):
        # 目录文件
        if self.name[0] == '\\':
            self.type = '.dir'

        else:
            type_loc = self.name.rfind('.')
            # 用户没有写文件后缀,或者'.'后为空
            if type_loc == -1 or self.name[-1] == '.':
                self.type = '.file'
                self.name=self.name+self.type
            # 用户书写了文件后缀
            else:
                self.type = self.name[type_loc:]

        # 文件创建时间
        self.ctime = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())
        # 文件的修改时间，初始化和创建时间相同
        self.mtime = self.ctime

    def update_content(self, content):
        self.content = content

    def update_size(self):
        self.size = len(self.content)

    # 更新修改时间
    def update_time(self):
        self.mtime = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())

    def empty_file(self):
        self.ctime = ''
        self.mtime = ''
        self.prmis = ''


class FCB:
    def __init__(self, name, loc):
        self.name = name  # 文件的名字
        self.loc = loc  # 文件在磁盘中位置，对应的磁盘块号

import os
import random
import sys

import matplotlib.pyplot as plt
from .viui import ViWindow
from colorama import Fore, init
from math import ceil
from .disk import *
from .filesystemui import *
from .newdirui import *
from PyQt5.QtWidgets import QMessageBox
from .fileattributeui import *

# 自动调回颜色
init(autoreset=True)


class FileManager:
    file_sep = os.sep  # 获取系统文件分隔符
    root_path = os.getcwd() + file_sep + 'OS_files'  # 根目录

    file_content_sig = QtCore.pyqtSignal(int, str, int)

    def __init__(self, track_number, sec_number, block_size):
        self.disk = Disk(track_number, sec_number, block_size)

        # 空文件时执行
        # self.disk.free_map[0][0] = 1
        # file = File('\\/')
        # file.loc.append(0)
        # file.empty_file()
        # self.disk.blocks[0][0].store_file(file)
        # self.file_dict = {'/': {}}

        # # 字典树初始化
        self.file_dict = self.init_file_dict()

        # 当前目录，初始化为根目录
        self.cur_dict = self.file_dict['/']
        self.cur_path = ['/']

        self.windows = []

    def file_visual(self):
        """生成文件浏览界面

        """
        path = self.show_cur_path()
        window = FileSystemUI()
        window.path_update(path)
        for i in self.cur_dict.keys():
            # 排除文件夹dict
            if not isinstance(self.cur_dict[i], dict):
                temp_fcb = self.cur_dict[i]
                temp_block = self.disk.loc_to_block(temp_fcb.loc)
                content = []

                if temp_block.file.type == '.dir':
                    file_name = temp_block.file.name[1:]
                    content.append(file_name)
                    content.append(temp_block.file.type)
                    content.append(temp_block.file.mtime)
                    content.append('     ')

                else:
                    content.append(temp_block.file.name)
                    content.append(temp_block.file.type)
                    content.append(temp_block.file.mtime)
                    content.append(str(temp_block.file.size) + 'Byte')

                window.addItem(content)

        window.listWidget.itemDoubleClicked.connect(lambda: self.item_double_clicked(window))
        window.path_btn.clicked.connect(lambda: self.path_back_btn_clicked(window))
        window.jmp_btn.clicked.connect(lambda: self.path_jmp_btn_clicked(window))
        window.open_sig.connect(lambda: self.item_double_clicked(window))
        window.new_dir_sig.connect(lambda: self.right_menu_new_dir(window))
        window.del_sig.connect(lambda: self.right_menu_del(window))
        window.new_file_sig.connect(lambda: self.right_menu_new_file(window))
        window.file_attribute_sig.connect(lambda: self.right_menu_attribute(window))

        window.show()

    def right_menu_attribute(self, window):
        listwidget = window.listWidget
        cur_item = listwidget.currentItem()
        item_widget = listwidget.itemWidget(cur_item)
        label_l = item_widget.findChildren(QLabel)
        file_name = label_l[1].text()
        file_type = label_l[2].text()

        if file_type == '.dir':
            file_name = '\\' + file_name

        temp_fcb = self.cur_dict[file_name]
        temp_block = self.disk.loc_to_block(temp_fcb.loc)

        dlg = FileAttributeUI()
        dlg.name_lineEdit.setText(label_l[1].text())
        dlg.type_lineEdit.setText(temp_block.file.type)
        dlg.sieze_lineEdit.setText(str(temp_block.file.size) + ' Byte')
        dlg.ctime_lineEdit.setText(temp_block.file.ctime)
        dlg.mtime_lineEdit.setText(temp_block.file.mtime)

        dlg.show()
        dlg.exec()

    def right_menu_new_file(self, window):
        dlg = NewDirUI()
        dlg.certain_btn.clicked.connect(lambda: self.new_file_certain_btn(dlg, window))
        dlg.show()
        dlg.exec()

    def new_file_certain_btn(self, dlg, window):
        file_name = dlg.filename_lineedit.text()
        self.mkf(file_name)
        self.window_update(window)
        dlg.close()

    def right_menu_del(self, window):
        """右键点击了删除按钮

        :param window: 当前窗口
        """
        listwidget = window.listWidget
        cur_item = listwidget.currentItem()
        item_widget = listwidget.itemWidget(cur_item)
        label_l = item_widget.findChildren(QLabel)
        file_name = label_l[1].text()

        ques_dlg = QMessageBox.question(None, "提示", "是否确认删除", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if ques_dlg == QMessageBox.Yes:
            self.rm(file_name)
            self.window_update(window)

    def right_menu_new_dir(self, window):
        """右键点击了新建文件夹按钮

        :param window: 当前的窗口
        """
        dlg = NewDirUI()
        dlg.certain_btn.clicked.connect(lambda: self.new_dir_certain_btn(dlg, window))
        dlg.show()
        dlg.exec()

    def new_dir_certain_btn(self, dlg, window):
        """右键点击了新建文件夹并且点击了确认按钮

        :param dlg: 当前的对话框
        :param window: 对话框依附的文件资源管理器窗口
        """
        dir_name = dlg.filename_lineedit.text()
        if not self.mkdir(dir_name):
            fail_msg = QMessageBox(QMessageBox.Warning, '警告', '文件夹已存在')
            fail_msg.exec()
        else:
            self.window_update(window)
            dlg.close()

    def window_update(self, window):
        """更新当前窗口内容

        :param window: 当前的窗口
        """
        path = self.show_cur_path()
        window.listWidget.clear()
        window.path_update(path)
        window.init_item()

        for i in self.cur_dict.keys():
            # 排除文件夹dict
            if not isinstance(self.cur_dict[i], dict):
                temp_fcb = self.cur_dict[i]
                temp_block = self.disk.loc_to_block(temp_fcb.loc)
                content = []

                if temp_block.file.type == '.dir':
                    file_name = temp_block.file.name[1:]
                    content.append(file_name)
                    content.append(temp_block.file.type)
                    content.append(temp_block.file.mtime)
                    content.append('     ')

                else:
                    content.append(temp_block.file.name)
                    content.append(temp_block.file.type)
                    content.append(temp_block.file.mtime)
                    content.append(str(temp_block.file.size) + 'Byte')

                window.addItem(content)

    def path_jmp_btn_clicked(self, window):
        path = window.path_lineedit.text()
        if self.cd(path):
            self.window_update(window)
        else:
            msg_dlg = QMessageBox(QMessageBox.Warning, '警告', '无效路径')
            msg_dlg.exec()

    def path_back_btn_clicked(self, window):
        """用户点击了文件资源管理器的路径返回按钮

        :param window: 传入的当前窗口
        """
        if len(self.cur_path) > 1:
            self.cur_path.pop()
            self.cur_dict = self.file_dict
            for i in self.cur_path:
                self.cur_dict = self.cur_dict[i]
        self.window_update(window)

    def item_double_clicked(self, window):
        """文件资源管理器的某一文件项被点击

        :param window: 当前窗口
        """
        listwidget = window.listWidget
        cur_item = listwidget.currentItem()
        item_widget = listwidget.itemWidget(cur_item)
        label_l = item_widget.findChildren(QLabel)
        file_name = label_l[1].text()
        file_type = label_l[2].text()

        if file_type == ".dir":
            self.cur_dict = self.cur_dict[file_name]
            self.cur_path.append(file_name)
            self.window_update(window)


        else:
            block = self.disk.loc_to_block(self.cur_dict[file_name].loc)
            file = block.file
            file.content = self.gather_file_content(file)
            # 实例化ViWindow对象
            vi_window = ViWindow(file.content)
            # save_signal信号连接槽函数
            vi_window.save_signal.connect(file.update_content)
            vi_window.save_signal.connect(file.update_time)

            # 将打开的文件窗口放入窗口字典中，防止子窗口实例销毁闪退

            vi_window.exec()
            # 文件内容更新
            file.update_size()
            # 文件块更新
            self.update_file_content(file)

            self.window_update(window)
            self.write_dict(self.file_dict)
            self.disk.write_block()

    def init_file_dict(self):  # 该函数是对目录进行初始化的操作
        temp_file_dict = dict()
        temp_file_dict['/'] = dict()
        with open('disk.txt') as f:
            self.deep_read(temp_file_dict, f)  # 通过递归进行文件的读取
        return temp_file_dict

    def deep_read(self, temp_dict, f_ptr):  # 文件读取的递归函数，参数分别是文件的指针以及此时要进行初始化的目录
        temp_data = f_ptr.readline()
        # if temp_data != '\n':
        temp_data = temp_data.rstrip()

        while temp_data != "":
            temp_list = temp_data.split(' ')
            if temp_list[0] == '$' or temp_list[0] == '----':
                # 当遇到$，表示此时该目录下的文件读取结束，需要返回上一级目录，当遇到----，表示目录部分的读取全部结束，文件内后面的数据为其他文件数据
                break
            elif temp_list[1] == 'next':  # 如果此时表中的值为next，则表示其为一个子目录，需要进行递归读取
                temp_dict[temp_list[0]] = dict()
                self.deep_read(temp_dict[temp_list[0]], f_ptr)
            else:
                temp_fcb = FCB(temp_list[1], int(temp_list[2]))
                temp_dict[temp_list[0]] = temp_fcb
            temp_data = f_ptr.readline()
            temp_data = temp_data.rstrip()



    def deep_write(self, temp_dict, f_ptr):  # 这里是写入文件的递归函数，参数分别是要写入文件的目录以及文件指针
        for item in temp_dict.items():
            if type(item[1]) == type(dict()):  # 如果是目录，表示此时需要进行递归，在进入之前将value部分写入next
                f_ptr.write(item[0])
                f_ptr.write(' next')
                f_ptr.write('\n')
                self.deep_write(item[1], f_ptr)
            else:
                f_ptr.write(item[0])
                f_ptr.write(' ')
                if type(item[1]) == type(FCB('0', 0)):
                    f_ptr.write(item[1].name)
                    f_ptr.write(' ')
                    f_ptr.write(str(item[1].loc))
                else:
                    f_ptr.write(str(item[1]))
                f_ptr.write('\n')
        f_ptr.write('$\n')  # 这里表示一层目录结束

    def write_dict(self, file_dict):  # 这里是将目录结构写入到文件中的操作，与读操作类似，依旧采用递归的方式来进行
        with open('disk.txt', 'w') as f:
            self.deep_write(file_dict, f)

    def ls(self, mode=''):
        """ls指令实现

        :param mode: mode为具体模式选择包含'','-a','-d','-l'
        """
        # 默认为空，只打印非隐藏目录和文件
        if mode == '':
            for i in self.cur_dict.keys():

                # 不为隐藏文件直接打印
                if i[0] != '.' and i[0] != '\\':

                    # 是文件夹,打印蓝色
                    if isinstance(self.cur_dict[i], dict):
                        print(Fore.BLUE + i, end=' ')
                    # 文件打印黑色
                    else:
                        print(i, end=' ')

        # -a 展示所有文件和目录，包括隐藏文件和目录
        elif mode == '-a':
            for i in self.cur_dict.keys():
                if i[0] != '\\':
                    # 是文件夹,打印蓝色
                    if isinstance(self.cur_dict[i], dict):
                        print(Fore.BLUE + i, end=' ')
                    # 文件打印黑色
                    else:
                        print(i, end=' ')

        # 只列出目录
        elif mode == '-d':
            for i in self.cur_dict.keys():
                if isinstance(self.cur_dict[i], dict):
                    print(Fore.BLUE + i, end=' ')

        # 以长格式显示文件和目录信息
        elif mode == '-l':
            for i in self.cur_dict:
                if isinstance(self.cur_dict[i], FCB):
                    block = self.disk.loc_to_block(self.cur_dict[i].loc)
                    block.file.show_basic_msg()
        print()

    # 到达指定目录处
    def cd(self, path=''):
        """前往指定目录处

        :param path: 传入路径
        :return: 无返回值
        """
        # 无参数
        if path == '':
            self.cur_path = ['/']
            self.cur_dict = self.file_dict['/']
            return
        # 参数为. 直接返回，展示当前目录
        if path == '.':
            return
        # 参数为.. 返回上一级目录
        if path == '..':
            if len(self.cur_path) > 1:
                self.cur_path.pop()
                self.cur_dict = self.file_dict
                for i in self.cur_path:
                    self.cur_dict = self.cur_dict[i]
            return

        # 根路径寻找
        if path[0] == '/':
            tmp_dict = self.file_dict['/']
            tmp_path = ['/']
            path = path.lstrip('/')

        # 相对路径寻找
        else:
            tmp_dict = self.cur_dict
            tmp_path = self.cur_path[:]

        if path == '':
            print('无效路径')
            return True

        # 路径切割
        path_list = path.split('/')
        for i in path_list:
            if i in tmp_dict.keys():
                if isinstance(tmp_dict[i], dict):
                    tmp_dict = tmp_dict[i]
                    tmp_path.append(i)
                else:
                    print('无效路径')
                    return False

            else:
                print('无效路径')
                return False

        self.cur_dict = tmp_dict
        self.cur_path = tmp_path
        return True

    def mkdir(self, name, mode='', prmis='rwe'):
        """创建目录

        :param name: 目录名称
        :param mode: 创建目录的模式，‘’，‘-t’
        :param prmis: 目录权限，默认为‘rwe’
        """
        if name in self.cur_dict.keys()and isinstance(self.cur_dict[name],dict):
            print('该目录已存在')
            return False
        else:
            # t模式要单独考虑
            if mode == '-t':
                # 直接删除原文件夹
                self.rm(name, '-f')

            # 磁盘分配一个块，返还该块和块号
            block, loc = self.disk.alloc_block()
            # 建立目录文件
            dir_name = '\\' + name
            file = File(dir_name, prmis=prmis)
            file.loc.append(loc)
            # 获取文件基本信息
            file.get_type_time()
            # 存入block
            block.store_file(file)
            # 建立目录文件的fcb
            fcb = FCB(name, loc)
            self.cur_dict[name] = dict()
            self.cur_dict[dir_name] = fcb
            return True

    def mkf(self, name, prmis='rwe'):
        """创建文件

        :param name:文件名称
        :param prmis: 文件访问权限，默认为‘rwe
        """
        if name == '':
            return False

        if name in self.cur_dict.keys()and isinstance(self.cur_dict[name],FCB):
            self.rm(name)

        # 磁盘分配一个块，返还改块和块号
        block, loc = self.disk.alloc_block()
        # 建立文件
        file = File(name, prmis=prmis)
        file.loc.append(loc)
        # 获取文件类型
        file.get_type_time()
        # 存入block
        block.store_file(file)
        # 建立FCB
        fcb = FCB(file.name, loc)
        self.cur_dict[file.name] = fcb
        return True

    # 删除文件或目录
    def rm(self, name, mode=''):
        """删除文件或目录

        :param name:删除的文件名或目录名
        :param mode: 删除模式
        """
        if mode == '' or mode == '-f':  # 将目录完全删除，包括其中的文件，并且需要将对应的FCB和block中的内容进行删除。
            # 删除对象存在于当前目录
            if name in self.cur_dict.keys():
                # 是目录
                if isinstance(self.cur_dict[name], dict):
                    # 递归删除目录
                    self.del_dir(self.cur_dict[name])
                    # 删除目录文件
                    dir_name = '\\' + name
                    temp_block = self.disk.loc_to_block(self.cur_dict[dir_name].loc)
                    temp_block.rm_file()
                    self.cur_dict.pop(dir_name)
                    self.cur_dict.pop(name)
                # 是文件
                else:
                    # 清空磁盘块中内容
                    file_block = self.disk.loc_to_block(self.cur_dict[name].loc)
                    file = file_block.file

                    for j in file.loc.__reversed__():
                        tmp_block = self.disk.loc_to_block(j)
                        tmp_block.rm_file()
                        self.disk.reset_map(j)
                    self.cur_dict.pop(name)

            else:
                print('无效目标')

    def del_dir(self, cur_dict):
        """递归删除文件夹和文件

        :param cur_dict: 当前的文件夹
        """
        for i in list(cur_dict.keys()):
            if isinstance(cur_dict[i], dict):
                self.del_dir(cur_dict[i])
                # 删除目录文件的信息
                cur_dict.pop(i)

            else:
                # 清空磁盘块中内容
                file_block = self.disk.loc_to_block(cur_dict[i].loc)
                file = file_block.file
                for j in file.loc.__reversed__():
                    tmp_block = self.disk.loc_to_block(j)
                    tmp_block.rm_file()
                    self.disk.reset_map(j)
                cur_dict.pop(i)

    def cat(self, name=''):
        """查看文件内容

        :param name: 文件名
        """
        if name in self.cur_dict.keys():
            if type(self.cur_dict[name]) == type(dict()):
                print('无法查看目录内容')
            else:
                temp_fcb = self.cur_dict[name]
                temp_block = self.disk.loc_to_block(temp_fcb.loc)

                print(self.gather_file_content(temp_block.file))

    # 打开编辑文件窗口
    def vi(self, name, file_content_sig, writeback):
        """打开文件编辑界面

        :param name:要打开的文件名
        """
        if name in self.cur_dict.keys() and isinstance(self.cur_dict[name], FCB):
            block = self.disk.loc_to_block(self.cur_dict[name].loc)
            file = block.file
            file.content = self.gather_file_content(file)

            con_l = []
            con_l.append(file.content)
            con_l.append(len(file.content))
            con_l.append(file.loc[0])

            file_content_sig.emit(-1, self.show_cur_path() + file.name, con_l)
            # 实例化ViWindow对象

            vi_window = ViWindow(file.content)
            self.windows.append(vi_window)
            # save_signal信号连接槽函数
            vi_window.save_signal.connect(file.update_content)
            vi_window.save_signal.connect(file.update_time)
            vi_window.exec()

            con_l = []
            con_l.append(file.content)
            con_l.append(len(file.content))
            con_l.append(file.loc[0])

            file_content_sig.emit(-1, self.show_cur_path() + file.name, con_l)
            writeback.emit(-1, self.show_cur_path() + file.name)
            # 文件内容更新
            file.update_size()
            # 文件块更新
            self.update_file_content(file)
        else:
            print('文件不存在')

    # 读取文件内容
    def gather_file_content(self, file=File()):
        """将分布于各个块的文件内容聚集起来

        :param file: 想要聚集内容的文件
        :return: 返回聚集的文件内容，为字符串
        """
        content = ''
        for i in file.loc:
            tmp_block = self.disk.loc_to_block(i)
            content += tmp_block.file.content
        return content

    # 当文件大小增加时，需要多分配块
    def update_file_content(self, file=File()):
        """更新各个块的文件内容

        :param file: 要更新内容的文件
        """
        alloc_num = len(file.loc)
        need_num = ceil(file.size / 20)
        if need_num == 0:
            need_num = 1
        # 需要增添块数
        if alloc_num < need_num:
            add_num = need_num - alloc_num
            for i in range(0, add_num):
                tmp_block, loc = self.disk.alloc_block()
                file.loc.append(loc)

        # 需要减少块数
        elif alloc_num > need_num:
            excess_num = alloc_num - need_num
            excess_l = []
            for i in range(0, excess_num):
                excess_l.append(file.loc.pop())

            # 清空磁盘块中内容
            for i in excess_l:
                tmp_block = self.disk.loc_to_block(i)
                tmp_block.rm_file()
                self.disk.reset_map(i)

        content = file.content
        for i in range(0, need_num):
            tmp_block = self.disk.loc_to_block(file.loc[i])
            if i == need_num - 1:
                tmp_block.file.content = content[i * 20:]
            else:
                tmp_block.file.content = content[i * 20:i * 20 + 20]

    def path_to_file(self, path):
        """外部得到文件内容

        :param path: 外部传来的绝对地址，带分隔符
        :return: 返回文件内容和内容大小组合成的列表，前者为字符串后者为int
        """
        tmp_dict = self.file_dict['/']
        path_list = path.split('/')
        # 路径
        for i in path_list[:-1]:
            if i in tmp_dict.keys():
                if isinstance(tmp_dict[i], dict):
                    tmp_dict = tmp_dict[i]
                    # 文件不存在
                else:
                    return -1

        if path_list[-1] in tmp_dict.keys() and isinstance(tmp_dict[path_list[-1]], FCB):
            block = self.disk.loc_to_block(tmp_dict[path_list[-1]].loc)
            content = self.gather_file_content(block.file)
            content_len = len(content)
            con_l = []
            con_l.append(content)
            con_l.append(content_len)
            con_l.append(tmp_dict[path_list[-1]].loc)
            return con_l
        else:
            return -1

    # 以字符串形式展示当前的路径
    def show_cur_path(self):
        """展示当前的路径

        :return: 返回当前路径的信息
        """
        # 只有一个属性直接返回根目录
        if len(self.cur_path) == 1:
            return '/'
        else:
            str_path = '/' + self.cur_path[1]
            for i in self.cur_path[2:]:
                str_path += '/' + i
            return str_path

    def bat_file(self, filename, content):
        """批处理文件修改文件内容

        :param filename: 要修改的文件名
        :param content: 要修改的内容
        :return: 无返回参数
        """
        if filename in self.cur_dict.keys():
            temp_fcb = self.cur_dict[filename]
            temp_block = self.disk.loc_to_block(temp_fcb.loc)
            temp_block.file.content = content
            self.update_file_content(temp_block.file)

        return

    def imt_disk_seek(self, method='SSTF'):
        """寻道模拟

        :param method:寻道方式
        """
        disk_l = [random.randint(1, 201) for i in range(0, 10)]
        final_list = list()
        times = 0
        now = random.randint(1, 201)

        if method == 'FCFS':
            for i in range(0, 10):
                times = times + abs(disk_l[i] - now)
                final_list.append(disk_l[i])
                now = disk_l[i]
            self.disk_seek_pic(final_list, times, 'FCFS')
        elif method == 'SSTF':
            disk_l.sort()
            number = 0
            location = 0
            for i in range(0, 10):
                if disk_l[i] >= now:
                    location = i
                    break
            low = now - disk_l[location - 1]
            high = disk_l[location] - now
            if low <= high:
                location = i - 1
            else:
                location = i
            while number <= 9:
                times = times + abs(disk_l[location] - now)
                now = disk_l[location]
                final_list.append(now)
                disk_l[location] = 100000
                Rtemp = location
                while Rtemp <= 9 and disk_l[Rtemp] == 100000:
                    Rtemp = Rtemp + 1
                Ltemp = location
                while Ltemp >= 0 and disk_l[Ltemp] == 100000:
                    Ltemp = Ltemp - 1
                if Rtemp > 9:
                    Rtemp = 9
                if Ltemp < 0:
                    Ltemp = 0
                low = abs(now - disk_l[Ltemp])
                high = abs(disk_l[Rtemp] - now)
                if low <= high:
                    location = Ltemp
                else:
                    location = Rtemp
                number = number + 1
            self.disk_seek_pic(final_list, times, 'SSTF')
        elif method == 'C_LOOK':
            disk_l.sort()
            number = 0
            location = 0
            for i in range(0, 10):
                if disk_l[i] >= now:
                    location = i
                    break
            while number <= 9:
                if location <= 9 and location >= i:
                    times = times + abs(disk_l[location] - now)
                    final_list.append(disk_l[location])
                    now = disk_l[location]
                    location = location + 1
                    if location == 10:
                        location = 0
                else:
                    times = times + abs(disk_l[location] - now)
                    final_list.append(disk_l[location])
                    now = disk_l[location]
                    location = location + 1
                number = number + 1
            self.disk_seek_pic(final_list, times, 'C_LOOK')
        elif method == 'LOOK':
            disk_l.sort()
            number = 0
            location = 0
            for i in range(0, 10):
                if disk_l[i] >= now:
                    location = i
                    break
            while number <= 9:
                if location <= 9 and location >= i:
                    times = times + abs(disk_l[location] - now)
                    final_list.append(disk_l[location])
                    now = disk_l[location]
                    location = location + 1
                    if location == 10:
                        location = i - 1
                else:
                    times = times + abs(disk_l[location] - now)
                    final_list.append(disk_l[location])
                    now = disk_l[location]
                    location = location - 1
                number = number + 1
            self.disk_seek_pic(final_list, times, 'LOOK')
        elif method == 'SCAN':
            disk_l.sort()
            number = 0
            location = 0
            for i in range(0, 10):
                if disk_l[i] >= now:
                    location = i
                    break
            while number <= 9:
                if location <= 9 and location >= i:
                    times = times + abs(disk_l[location] - now)
                    final_list.append(disk_l[location])
                    now = disk_l[location]
                    location = location + 1
                    if location == 10:
                        now = 200
                        times = times + 200 - disk_l[9]
                        final_list.append(200)
                        location = i - 1
                else:
                    times = times + abs(disk_l[location] - now)
                    final_list.append(disk_l[location])
                    now = disk_l[location]
                    location = location - 1
                number = number + 1
            self.disk_seek_pic(final_list, times, 'SCAN')
        elif method == 'C_SCAN':
            disk_l.sort()
            number = 0
            location = 0
            for i in range(0, 10):
                if disk_l[i] >= now:
                    location = i
                    break
            while number <= 9:
                if location <= 9 and location >= i:
                    times = times + abs(disk_l[location] - now)
                    final_list.append(disk_l[location])
                    now = disk_l[location]
                    location = location + 1
                    if location == 10:
                        now = 200
                        times = times + 200 - disk_l[9]
                        final_list.append(200)
                        times = times + 200
                        final_list.append(0)
                        location = 0
                else:
                    times = times + abs(disk_l[location] - now)
                    final_list.append(disk_l[location])
                    now = disk_l[location]
                    location = location + 1
                number = number + 1
            self.disk_seek_pic(final_list, times, 'C_SCAN')

    def disk_seek_pic(self, way=[], times=0, title=''):
        """画寻道图

        :param way:寻道的x轴
        :param times: 寻道次数
        :param tittle: 寻道方法
        """
        flag = 1
        flag1 = 11
        if title == 'SCAN' or title == 'C_SCAN':
            flag = 0
            if title == 'C_SCAN':
                flag1 = flag1 + 1

        y_axis = [i for i in range(flag, flag1)]
        plt.yticks(y_axis)
        title = title + '  ' + str(times)
        plt.title(title)
        for a, b in zip(way, y_axis):
            plt.text(a, b, a, ha='center', va='bottom', fontsize=10)
        plt.plot(way, y_axis, marker='o', label='track number', alpha=0.5)
        plt.legend(loc='best')
        plt.show()


if __name__ == '__main__':
    test_file_manager = FileManager(20, 10, 512)

    cmd = input(f'{test_file_manager.show_cur_path()} >>>')
    while cmd != 'exit':
        if cmd[0:2] == 'ls':
            cmd = cmd[2:]
            test_file_manager.ls(cmd)
        elif cmd[0:2] == 'cd':
            cmd = cmd[2:]
            test_file_manager.cd(cmd)
        elif cmd[0:3] == 'mkf':
            test_file_manager.mkf(cmd[3:])
        elif cmd[0:2] == 'vi':
            test_file_manager.vi(cmd[2:])

        elif cmd[0:5] == 'mkdir':
            test_file_manager.mkdir(cmd[5:])

        elif cmd[0:3] == 'cat':
            test_file_manager.cat(cmd[3:])

        elif cmd[0:2] == 'rm':
            test_file_manager.rm(cmd[2:])

        elif cmd[0:7] == 'dseek ':
            test_file_manager.imt_disk_seek(cmd[7:])

        cmd = input(f'{test_file_manager.show_cur_path()} >>>')

    # test_file_manager.imt_disk_seek('f')
    # test_file_manager.bat_file('ile', '333')
    # print(test_file_manager.path_to_file('111/222/333.txt'))

    app = QApplication(sys.argv)
    test_file_manager.file_visual()
    app.exec()

    test_file_manager.path_to_file('1')

    test_file_manager.write_dict(test_file_manager.file_dict)
    test_file_manager.disk.write_block()

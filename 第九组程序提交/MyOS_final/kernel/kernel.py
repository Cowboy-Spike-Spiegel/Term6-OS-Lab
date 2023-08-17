# coding=utf-8
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from colorama import init

import Process_Init
from file_manager import file_manager
from memory_manager import MemoryManager
from process_manager import process_manager
from .shell import Shell
import threading


# from process_manager.device import Device_Manager


class Kernel:
    # 初始化
    def __init__(self,option):
        self.my_shell = Shell()
        self.my_file_manager = file_manager.FileManager(20, 10, 512)
        self.my_memory_manager = MemoryManager(pageSize=16, pageNum=128, step=2, orderLen=4)
        self.option = option
        self.my_process_manager = process_manager(self.my_memory_manager, self.option)
        '''option = input("欢迎使用Myos，请选择您想使用的进程调度算法（优先级抢占（e）、FCFS（f）、RR（r）、优先级非抢占（p）\n")
        if option == 'e':
            option = "Preemptive Priority"
        elif option == 'f':
            option = "FCFS"
        elif option == 'r':
            option = "RR"
        elif option == 'p':
            option = "Non-preemptive Priority"
        else:
            option = input("输入不合法，请重新选择\n")
        
        self.my_device_manager = Device_Manager.DeviceManager()
        # 运行进程模块'''

    # 用户输入指令不存在时提供错误信息
    def report_error(self, cmd, err_msg='', window = None):
        put = '[error '+str(cmd)+']: '+str(err_msg)
        window.signals.text_print.emit(window.textEdit, put)
        print('[error %s]: %s' % (cmd, err_msg))
        if err_msg == '':
            self.display_command_description(cmd_list=[cmd],window=window)

    # help指令，展示所有指令及用法，也可以通过: help [cmd1] [cmd2] ...的形式精确查找一条指令的用法
    # 同时，display方法中的command_description字典里的key作为所有可执行指令的集合，用来分析用户输入的指令是否正确合法
    def display_command_description(self, cmd_list,window):
        command_description = {
            'help': '展示所有指令的用途，format: help [command1] [command2] ...',
            'ls': '列出目录内容，format: ls [ ]/[-a]/[-d]/[-l]',
            'cd': '更改当前目录，format: cd [path]/[.]/[..]',
            'rm': '册除文件或目录,format: rm[-f]/[ ] path',
            'mkdir': '创建新目录，format: mkdir [ ]/[-t] [name]',
            'mkf': '创建新文件, format: mkf [name]',
            'vi': '编辑文件,format: vi [filename]',
            'cat': '显示文件内容, format: cat [filename]',
            'save': '保存更改的所有文件信息，format: save',
            'dseek': '寻道模拟， format: dseek [method]',
            'exec': '创建进程并执行用户所指定的文件路径的文件内容, format: exec path [ ]/[-f]/[-r]/[-p]',
            'test': '创建一个最高优先级的进程来测试进程的调度，与exec格式相同, format: test path',
            'snapshot': '展示并发进程状态, format: snapshot',
            'kill': '强制终止进程, format: kill pid',
            'device': '显示设备管理器的信息,format: device show',
            'display ': '展示系统虚拟内存(-v)和物理内存(-p)的占用状态, format: display [-v]/[-p]',
            'exit': '退出MyOS并且再次保存一下所有文件信息, format: exit'
        }
        # help功能中查找某一条指令用法的实现
        if len(cmd_list) == 0:
            cmd_list = command_description.keys()
        for cmd in cmd_list:
            if cmd in command_description.keys():
                print(cmd, '-', command_description[cmd])
            else:
                self.report_error(cmd=cmd, err_msg='There is no such command！',window=window)

    def run(self, command, window):
        command_split_list = self.my_shell.get_split_command(command)
        # 输入为空
        if len(command_split_list) == 0:
            print("指令为空")
        # # 打印用户输入的指令
        # print('用户输入的指令是：')
        # for command_split in command_split_list:
        #     print(command_split)

        for command_split in command_split_list:
            if len(command_split) == 0:  # 空指令
                continue
            tool = command_split[0]  # 指令名称, e.g. ls, cd, ...

            argc = len(command_split)  # 这条指令的字符串数，e.g.ls -a指令，argc为2

            if tool == 'help':
                self.display_command_description(cmd_list=command_split[1:])

            elif tool == 'ls':
                if argc == 2:
                    self.my_file_manager.ls(mode=command_split[1])
                elif argc == 1:
                    self.my_file_manager.ls(mode='')

            elif tool == 'cd':
                if argc == 2:
                    self.my_file_manager.cd(command_split[1])

            elif tool == 'rm':
                if argc == 3:
                    self.my_file_manager.rm(name=command_split[2], mode=command_split[1])
                elif argc == 2:
                    self.my_file_manager.rm(name=''.join(command_split[1:]), mode='')

            elif tool == 'mkf':
                if argc == 2:
                    self.my_file_manager.mkf(name=command_split[1], prmis='rwe')

            elif tool == 'mkdir':
                if argc == 3:
                    self.my_file_manager.mkdir(name=command_split[2], mode=command_split[1])
                elif argc == 2:
                    self.my_file_manager.mkdir(name=command_split[1], mode='')

            elif tool == 'vi':
                if argc == 2:

                    self.my_file_manager.vi(command_split[1], window.signals.filesignals, window.signals.writeback)

            elif tool == 'cat':
                if argc == 2:
                    self.my_file_manager.cat(name=command_split[1])

            elif tool == 'save':
                self.my_file_manager.write_dict(self.my_file_manager.file_dict)
                self.my_file_manager.disk.write_block()

            elif tool == 'dseek':
                if argc == 2:
                    self.my_file_manager.imt_disk_seek(command_split[1])

            elif tool == 'exec':
                if argc == 2:
                    self.my_process_manager.create_process(command_split[1], window)

            elif tool == 'test':
                if argc == 2:
                    self.my_process_manager.create(command_split[1], window)

            elif tool == 'snapshot':
                if argc == 1:
                    self.my_process_manager.snapshot(window)

            elif tool == 'kill':
                if argc == 2:
                    self.my_process_manager.kill(int(command_split[1]), window)

            elif tool == 'device':
                print("device")
                # if ''.join(command_split[1:]) == 'show':
                #     self.my_device_manager.look_state()

            elif tool == 'display':
                if command_split[1] == '-v':
                    self.my_memory_manager.draw_memory(1)
                elif command_split[1] == '-p':
                    self.my_memory_manager.draw_memory(2)

            elif tool == 'exit':
                self.my_file_manager.write_dict(self.my_file_manager.file_dict)
                self.my_file_manager.disk.write_block()
                exit(0)

            else:
                self.report_error(cmd=tool, err_msg='There is no such command！',window=window)


if __name__ == '__main__':
    init(autoreset=True)  # 多颜色输出
    my_kernel = Kernel()
    my_kernel.run()

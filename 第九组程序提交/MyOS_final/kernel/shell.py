# coding=utf-8

import datetime


class Shell:
    def __init__(self):
        self.print_system_info()

    def print_system_info(self):
        print('MyOS 1.0', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # 获取用户输入的指令
    def get_split_command(self, command):
        try:
            # 用户输入的指令间以分号分隔
            commands = command.split(';')
        except BaseException:
            commands = []
        for i in range(len(commands)):
            # 指令间的字符串以空格或tab分隔
            raw_command = commands[i].split()
            if len(raw_command) == 0:
                continue
            commands[i] = [raw_command[0]]
            for arg in raw_command[1:]:
                commands[i].append(arg)
        return commands

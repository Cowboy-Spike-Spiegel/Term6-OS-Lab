from process_manager import constants
from .device import MessageUnit, DeviceManager
import queue
import random
import datetime
import time
import threading
import matplotlib.pyplot as plt
import warnings

# 忽略警告信息
warnings.filterwarnings('ignore', category=UserWarning)


class PCB:
    def __init__(self, ppid=constants.OS_CREATE, pid=0, priority=20, ctime="", size=0, type=constants.OS_CREATE, pc=-1,
                 total_line=0):
        """
        :param ppid:进程的父进程id
        :param pid:进程的pid
        :param priority:进程的优先级
        :param ctime:进程的创建时间
        :param size:进程的大小
        :param type:进程是由操作系统创建的还是由fork创建的，0代表操作系统，1代表fork
        :param pc:进程的程序计数器
        :param total_line:进程的总代码行数
        """
        self.ppid = ppid
        self.pid = pid
        self.priority = priority
        self.pc = pc
        self.ctime = ctime
        self.size = size
        self.type = type
        self.status = "ready"
        self.total_line = total_line

    # 用于输出进程信息
    def __str__(self):
        string = "进程ID：{}".format(self.pid) + '\t' + \
                 "进程父ID：{}".format(self.ppid) + '\t' + \
                 "进程优先级：{}".format(self.priority) + '\t' + \
                 "\n进程状态：{}".format(self.status) + '\t' + \
                 "进程创建时间：{}".format(self.ctime)
        return string

    # 进行同类比较的方法，用于进程优先级的比较
    def __lt__(self, other):
        """
        :param other:其它同类进程
        """
        if self.priority == other.priority:
            return self.pid < other.pid
        return self.priority < other.priority

    # 判断相等的方法，用于释放PCB资源
    def __eq__(self, other):
        """
        :param other: 其它同类进程
        """
        if self.pid == other.pid:
            return True
        return False


class process_manager:
    def __init__(self, memory_manager, algorithm="Preemptive Priority"):
        """
        :param memory_manager:内存管理的实例化对象
        :param algorithm:调度算法，默认是优先级抢占
        """
        self.cur_pid = constants.DEFAULT_PID  # 当前分配的pid
        if algorithm == "FCFS" or algorithm == "RR":
            self.ready_queue = []
        elif algorithm == "Preemptive Priority" or algorithm == "Non-preemptive Priority":
            self.ready_queue = queue.PriorityQueue()
        self.algorithm = algorithm
        self.memory_manager = memory_manager
        self.cur_process = PCB()  # 用来记录当前正在运行的进程
        self.pcb_list = []  # 记录进程队列
        self.pcb_max = constants.DEFAULT_MAX  # pcb队列的最大长度
        self.new_process = constants.NO_NEW_PROCESS  # 记录是否有新进程加入
        self.waiting_queue = []
        self.device_manager = DeviceManager()
        self.record = {}  # 记录进程使用情况的字典
        self.sys_time = 0  # 记录系统时间信息
        self.cpu_record = []  # 记录cpu的使用情况
        self.IO_record = {}  # 记录IO的使用情况

    # 判断就绪队列是否为空
    def is_null(self):
        if self.algorithm == "FCFS" or self.algorithm == "RR":
            if len(self.ready_queue) == constants.EMPTY:
                return True
            else:
                return False
        elif self.algorithm == "Preemptive Priority" or self.algorithm == "Non-preemptive Priority":
            if self.ready_queue.empty():
                return True
            else:
                return False

    # 添加新进程
    def add_process(self, process):
        if self.algorithm == "FCFS" or self.algorithm == "RR":
            self.ready_queue.append(process)
        elif self.algorithm == "Preemptive Priority" or self.algorithm == "Non-preemptive Priority":
            self.ready_queue.put_nowait(process)

    # 创建进程，由CPU创建出来的进程，ppid默认是0
    def create_process(self, path, window):
        """
        :param window: 窗口参数
        :param path:进程文件路径
        """
        # 看pcb_list有没有满，再看内存是否有足够的空间分配
        if len(self.pcb_list) <= self.pcb_max:
            size = self.memory_manager.alloc(path, self.cur_pid, window)
            if size != constants.ERROR:
                # 优先级采用随机数的方式生成，值越小优先级越高
                priority = random.randint(constants.MAX_PRIORITY, constants.MIN_PRIORITY)
                ctime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                process = PCB(constants.OS_CREATE, self.cur_pid, priority, ctime, size, constants.OS_CREATE,
                              constants.PC_BEGIN, size / constants.ORDER_LENGTH)
                self.add_process(process)
                self.pcb_list.append(process)
                # 告知系统有新进程加入
                if self.new_process == constants.NO_NEW_PROCESS:
                    self.new_process = constants.NEW_PROCESS
                put = "Process[" + str(self.cur_pid) + "] created successfully!"
                window.signals.text_print.emit(window.textEdit, put)
                print("Process[%d] created successfully!" % self.cur_pid)
                self.cur_pid = self.cur_pid + 1
            else:
                put = "Failed to allocate enough memory or the target file does not exist!"
                window.signals.text_print.emit(window.textEdit, put)
                print("Failed to allocate enough memory or the target file does not exist!")
        else:
            put = "There is no vacancy in pcb_list!"
            window.signals.text_print.emit(window.textEdit, put)
            print("There is no vacancy in pcb_list!")

    # 固定创建一个优先级最高的进程（优先级为1）（用于测试进程调度）
    def create(self, path, window):
        """
        :param window: 窗口指针
        :param path:进程文件路径
        """
        # 看pcb_list有没有满，再看内存是否有足够的空间分配
        if len(self.pcb_list) <= self.pcb_max:
            size = self.memory_manager.alloc(path, self.cur_pid, window)
            if size != constants.ERROR:
                priority = constants.MAX_PRIORITY  # 优先级固定为最高优先级
                ctime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                process = PCB(constants.OS_CREATE, self.cur_pid, priority, ctime, size, constants.OS_CREATE,
                              constants.PC_BEGIN, size / constants.ORDER_LENGTH)
                self.add_process(process)
                self.pcb_list.append(process)
                # 告知系统有新进程加入
                if self.new_process == constants.NO_NEW_PROCESS:
                    self.new_process = constants.NEW_PROCESS
                put = "Process[" + str(self.cur_pid) + "] created successfully!"
                window.signals.text_print.emit(window.textEdit, put)
                print("Process[%d] created successfully!" % self.cur_pid)
                self.cur_pid = self.cur_pid + 1
            else:
                put = "Failed to allocate enough memory!"
                window.signals.text_print.emit(window.textEdit, put)
                print("Failed to allocate enough memory!")
        else:
            put = "There is no vacancy in pcb_list!"
            window.signals.text_print.emit(window.textEdit, put)
            print("There is no vacancy in pcb_list!")

    # fork原语，用于创建一个进程，进程的ppid继承自父进程
    def fork(self, process, window):
        """
        :param process: 父进程
        """
        if len(self.pcb_list) <= self.pcb_max:
            result = self.memory_manager.alloc_fork(process.pid, self.cur_pid)
            if result != constants.ERROR:
                ctime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                child_process = PCB(process.pid, self.cur_pid, process.priority, ctime, process.size,
                                    constants.FORK_CREATE, process.pc + 1, process.total_line)  # pid继承自父进程
                self.add_process(child_process)
                self.pcb_list.append(child_process)
                # 告知系统有新进程加入
                if self.new_process == constants.NO_NEW_PROCESS:
                    self.new_process = constants.NEW_PROCESS
                put = "Process[" + str(self.cur_pid) + "] created successfully!"
                window.signals.text_print.emit(window.textEdit, put)
                print("Process[%d] created successfully!" % self.cur_pid)
                self.cur_pid = self.cur_pid + 1
            else:
                put = "Failed to allocate enough memory!"
                window.signals.text_print.emit(window.textEdit, put)
                print("Failed to allocate enough memory!")
        else:
            put = "There is no vacancy in pcb_list!"
            window.signals.text_print.emit(window.textEdit, put)
            print("There is no vacancy in pcb_list!")

    # 进程调度，初次调度和抢占调度
    def schedule(self):
        if self.new_process != constants.NO_NEW_PROCESS:
            if self.algorithm == "Preemptive Priority":
                if not self.ready_queue.empty():
                    process = self.ready_queue.get()
                    if self.cur_process.priority <= process.priority:  # 优先级不如当前则正在执行的进程不变
                        self.ready_queue.put_nowait(process)
                    else:  # 优先级比当前进程高则抢占当前进程
                        if self.cur_process.pid != constants.EMPTY:
                            self.cpu_record.append([self.cur_process.pid, self.sys_time])  # 记录上一进程的结束信息
                            self.cur_process.status = "ready"
                            self.ready_queue.put_nowait(self.cur_process)
                        self.cur_process = process
                        self.cpu_record.append([self.cur_process.pid, self.sys_time])  # 记录下一进程的开始信息
                        self.cur_process.status = "running"
                self.new_process = constants.NO_NEW_PROCESS  # 当前所有新加入进程都判断完成
            elif self.algorithm == "RR":
                if len(self.ready_queue) != constants.EMPTY:
                    process = self.ready_queue.pop(constants.READY_QUEUE_TOP)
                    if self.cur_process.pid != constants.EMPTY:
                        self.cpu_record.append([self.cur_process.pid, self.sys_time])  # 记录上一进程结束信息
                        self.cur_process.status = "ready"
                        self.ready_queue.append(self.cur_process)
                    self.cur_process = process
                    self.cpu_record.append([self.cur_process.pid, self.sys_time])  # 记录下一进程开始信息
                    self.cur_process.status = "running"
            else:
                # 对于FCFS和优先级非抢占，如果当前没有进程在跑则从就绪队列中获取一个进程
                if self.cur_process.pid == constants.EMPTY:
                    process = PCB()
                    if self.algorithm == "FCFS":
                        if len(self.ready_queue) != constants.EMPTY:
                            process = self.ready_queue.pop(constants.READY_QUEUE_TOP)
                    elif self.algorithm == "Non-preemptive Priority":
                        if not self.ready_queue.empty():
                            process = self.ready_queue.get()
                    self.cur_process = process
                    self.cpu_record.append([self.cur_process.pid, self.sys_time])  # 记录第一个进程的开始信息
                    self.cur_process.status = "running"

    # 唤醒waiting队列中的进程
    def awake(self, pid):
        # 从等待队列中删除对应进程
        target_process = PCB()
        for process in self.waiting_queue:
            if process.pid == pid:
                self.waiting_queue.remove(process)
                target_process = process
                break

        # 本次IO记录结束
        self.IO_record[target_process.pid][constants.END][constants.IO_END_TIME] = self.sys_time
        target_process.status = "ready"

        # 告知系统有新进程加入
        if self.new_process == constants.NO_NEW_PROCESS:
            self.new_process = constants.NEW_PROCESS
        self.add_process(target_process)

    # 结束当前进程
    def end_process(self):
        # 删除相关记录信息
        index = constants.INIT
        del_list = []
        for item in self.cpu_record:  # 已经走到end的进程不会再使用系统资源，因此删除所有相关记录
            if item[constants.CPU_RECORD_PID] == self.cur_process.pid:
                del_list.append(index)
            index += 1
        self.cpu_record = [i for num, i in enumerate(self.cpu_record) if num not in del_list]
        if self.cur_process.pid in self.IO_record.keys():
            self.IO_record.pop(self.cur_process.pid)

        # end处理
        if self.is_null():
            self.cur_process = PCB()  # 就绪队列为空则cur_process改为默认值
        else:
            if self.algorithm == "FCFS" or self.algorithm == "RR":
                self.cur_process = self.ready_queue.pop(constants.READY_QUEUE_TOP)
            elif self.algorithm == "Preemptive Priority" or self.algorithm == "Non-preemptive Priority":
                self.cur_process = self.ready_queue.get()
            self.cur_process.status = "running"
            self.cpu_record.append([self.cur_process.pid, self.sys_time])  # 记录当前进程的开始时间

            if self.algorithm == "RR":
                return True  # 跳过一次轮询的schedule
            return False

    # 执行进程内的代码
    def run(self, window):
        flag = False
        # 时钟中断
        time.sleep(constants.TIME_SLOT)
        self.sys_time += 1

        # 设备运行
        self.device_manager.run()
        rt_information, rt_error = self.device_manager.send_take()
        for item in rt_information:
            if item.state != "Has been killed":
                self.awake(item.number)
        self.device_manager.clear_afterSend()

        if self.cur_process.pc != constants.ERROR and self.cur_process.pc < self.cur_process.total_line:
            command = self.memory_manager.access(self.cur_process.pid, self.cur_process.pc * constants.ORDER_LENGTH,
                                                 constants.ORDER_LENGTH)
            # 将指令字符串转为列表
            order = command.split()
            if order[constants.INSTRUCTION] == "cpu":
                order[constants.PARAM1] = int(order[constants.PARAM1])
            # fork指令处理
            if order[constants.INSTRUCTION] == "fork":
                self.fork(self.cur_process, window)
                self.cur_process.pc += 1
            # cpu指令处理，cpu time
            elif order[constants.INSTRUCTION] == "cpu":
                # 为当前进程创建一条cpu使用记录，每进行一次时钟周期记录时间减1，cpu时间没用完则不会进行下一条指令
                if self.record.get(self.cur_process.pid) is None:
                    self.record[self.cur_process.pid] = order[constants.PARAM1]
                self.record[self.cur_process.pid] -= 1
                if self.record[self.cur_process.pid] == constants.EMPTY:
                    del self.record[self.cur_process.pid]
                    self.cur_process.pc += 1
                    put = "Process[" + str(self.cur_process.pid) + "] cpu done"
                    window.signals.text_print.emit(window.textEdit, put)
                    print("Process[%d] cpu done" % self.cur_process.pid)
                else:
                    put = "Process[" + str(self.cur_process.pid) + "] is using cpu " + str(
                        self.record[self.cur_process.pid])
                    window.signals.text_print.emit(window.textEdit, put)
                    print("Process[%d] is using cpu %d" % (self.cur_process.pid, self.record[self.cur_process.pid]))
            # read指令处理，read filename
            elif order[constants.INSTRUCTION] == "read":
                # 将文件名交给内存，拿到文件内容或报错信息
                filename = order[constants.PARAM1]
                content = self.memory_manager.read_file(self.cur_process.pid, filename, filename,window)
                if content != constants.ERROR:
                    window.signals.text_print.emit(window.textEdit, content)
                    print(content)
                else:
                    put = "The target file does not exist!"
                    window.signals.text_print.emit(window.textEdit, put)
                    print("The target file does not exist!")
                self.cur_process.pc += 1
            # end指令处理
            elif order[constants.INSTRUCTION] == "end":
                self.cur_process.status = "terminated"
                self.pcb_list.remove(self.cur_process)  # 从pcb_list中删除当前进程
                self.memory_manager.freeAllMem(self.cur_process.pid)  # 释放内存资源
                put = "Process[" + str(self.cur_process.pid) + "] has finished!"
                window.signals.text_print.emit(window.textEdit, put)
                print("Process[%d] has finished!" % self.cur_process.pid)
                if self.end_process():
                    flag = True
            # 外设指令处理 output info
            elif order[constants.INSTRUCTION] == "output":
                # 如果IO记录中没有当前的IO使用信息则创建一个
                if self.cur_process.pid not in self.IO_record.keys():
                    self.IO_record[self.cur_process.pid] = []
                self.IO_record[self.cur_process.pid].append([self.sys_time, constants.END])
                self.cur_process.status = "waiting"  # 修改当前进程状态
                self.waiting_queue.append(self.cur_process)  # 将当前进程放入等待队列
                self.cpu_record.append([self.cur_process.pid, self.sys_time])  # 记录当前进程的cpu结束时间
                # 交给设备处理
                clock = len(order[constants.PARAM1]) / 4
                self.device_manager.task_add(
                    MessageUnit(order[constants.INSTRUCTION], self.cur_process.pid, order[constants.PARAM1], clock))
                self.cur_process.pc += 1
                # 从就绪队列中调入新的进程
                if self.is_null():
                    self.cur_process = PCB()  # 就绪队列为空则cur_process改为默认值
                else:
                    if self.algorithm == "FCFS" or self.algorithm == "RR":
                        self.cur_process = self.ready_queue.pop(constants.READY_QUEUE_TOP)
                    elif self.algorithm == "Preemptive Priority" or self.algorithm == "Non-preemptive Priority":
                        self.cur_process = self.ready_queue.get()
                    self.cur_process.status = "running"
                    self.cpu_record.append([self.cur_process.pid, self.sys_time])  # 记录当前进程的开始时间
                    if self.algorithm == "RR":
                        flag = True
            # 错误
            else:
                put = "Error!"
                window.signals.text_print.emit(window.textEdit, put)
                print("Error!")
        # 源进程文件中没有end指令，运行到文件尾时自动执行end
        elif self.cur_process.pc == self.cur_process.total_line:
            self.cur_process.status = "terminated"
            self.pcb_list.remove(self.cur_process)  # 从pcb_list中删除当前进程
            self.memory_manager.freeAllMem(self.cur_process.pid)  # 释放内存资源
            put = "Process[" + str(self.cur_process.pid) + "] has finished!"
            window.signals.text_print.emit(window.textEdit, put)
            print("Process[%d] has finished!" % self.cur_process.pid)
            if self.end_process():
                flag = True
        if flag == False:
            self.schedule()

    # 强制kill一个进程
    def kill(self, pid, window):
        """
        :param window: 窗口指针
        :param pid: 进程的pid编号
        """
        exist = False  # 判断pid是否存在的标志位
        for item in self.pcb_list:
            if item.pid == pid:
                exist = True
                if pid == self.cur_process.pid:  # 如果是正在执行的进程就像当于提前执行end指令
                    self.cur_process.status = "terminated"
                    self.pcb_list.remove(self.cur_process)  # 从pcb_list中删除当前进程
                    self.memory_manager.freeAllMem(self.cur_process.pid)  # 释放内存资源
                    self.end_process()
                    put = "Process[" + str(pid) + "] has been killed!"
                    window.signals.text_print.emit(window.textEdit, put)
                    print("Process[%d] has been killed!" % pid)
                else:
                    item.status = "terminated"
                    # 删除相关记录信息
                    index = constants.INIT
                    del_list = []
                    for record in self.cpu_record:
                        if record[constants.CPU_RECORD_PID] == pid:
                            del_list.append(index)
                        index += 1
                    self.cpu_record = [i for num, i in enumerate(self.cpu_record) if num not in del_list]
                    if pid in self.IO_record.keys():
                        self.IO_record.pop(pid)

                    self.pcb_list.remove(item)  # 从pcb_list中删除当前进程
                    self.memory_manager.freeAllMem(item.pid)  # 释放内存资源
                    temp = []
                    flag = False  # 判断进程是否在等待队列的标志位
                    if self.algorithm == "FCFS" or self.algorithm == "RR":
                        for process in self.ready_queue:
                            if process.pid == pid:
                                flag = True
                                self.ready_queue.remove(process)
                                break
                    elif self.algorithm == "Preemptive Priority" or self.algorithm == "Non-preemptive Priority":
                        while not self.ready_queue.empty():  # 将进程踢出就绪队列
                            process = self.ready_queue.get()
                            if process.pid != pid:
                                temp.append(process)
                            else:
                                flag = True
                                break
                        for i in temp:  # 将拿出来的进程重新放回就绪队列中
                            self.ready_queue.put_nowait(i)

                    if not flag:  # 进程在等待队列中
                        for process in self.waiting_queue:
                            if process.pid == pid:
                                self.waiting_queue.remove(process)
                                break
                        self.device_manager.kill_add(pid)  # 告知设备也要kill
                    put = "Process[" + str(pid) + "] has been killed!"
                    window.signals.text_print.emit(window.textEdit, put)
                    print("Process[%d] has been killed!" % pid)
        if not exist:
            put = "Process[" + str(pid) + "] does not exist!"
            window.signals.text_print.emit(window.textEdit, put)
            print("Process[%d] does not exist!" % pid)

    # 展示进程当前的状态
    def snapshot(self, window):
        num = constants.EMPTY
        for item in self.pcb_list:
            put = str(item)
            window.signals.text_print.emit(window.textEdit,put)
            print(item)
            num += 1
        if num == constants.EMPTY:
            print("yes")
            put = "No process is ready, running or waiting!"
            window.signals.text_print.emit(window.textEdit, put)
            print("No process is ready, running or waiting!")
        else:  # 绘制Gantt图
            # 截至到当前时刻
            flag = False  # 判断当前cpu是否正在使用的标志
            if len(self.cpu_record) % 2 != 0:
                self.cpu_record.append([self.cur_process.pid, self.sys_time])
                flag = True
            for item in self.waiting_queue:
                self.IO_record[item.pid][constants.END][constants.IO_END_TIME] = self.sys_time

            # # 用于测试
            # for item in self.cpu_record:
            #     print("%d %d" % (item[0], item[1]))

            # 绘图信息
            plt.rcParams['backend'] = 'TkAgg'  # 取消SciView显示
            plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文标签
            fontdict_time = {
                "family": "Microsoft YaHei",
                "style": "oblique",
                "color": "black",
                "size": 10
            }
            plt.figure(num='Gantt图')

            # 绘制CPU的Gantt图
            n = constants.INIT
            while n < len(self.cpu_record):
                width = self.cpu_record[n + 1][constants.CPU_END_TIME] - self.cpu_record[n][constants.CPU_BEGIN_TIME]
                image1, = plt.barh(y=self.cpu_record[n][constants.CPU_RECORD_PID], width=width,
                                   left=self.cpu_record[n][constants.CPU_BEGIN_TIME], color='#00BFFF',
                                   edgecolor="black", height=0.6)
                plt.text(self.cpu_record[n][constants.CPU_BEGIN_TIME],
                         self.cpu_record[n][constants.CPU_RECORD_PID] - 0.05,
                         str(self.cpu_record[n][constants.CPU_BEGIN_TIME]) + "~" + str(
                             self.cpu_record[n + 1][constants.CPU_END_TIME]), fontdict=fontdict_time)
                n += 2

            # 绘制IO设备的Gantt图
            for pid, info in self.IO_record.items():
                for item in info:
                    width = item[constants.IO_END_TIME] - item[constants.IO_BEGIN_TIME]
                    image2, = plt.barh(y=pid, width=width, left=item[constants.IO_BEGIN_TIME], color='#FFFF00',
                                       edgecolor="black", height=0.6)
                    plt.text(item[constants.IO_BEGIN_TIME], pid - 0.05,
                             str(item[constants.IO_BEGIN_TIME]) + "~" + str(item[constants.IO_END_TIME]),
                             fontdict=fontdict_time)

            # 完成绘图后还要恢复原信息
            if flag:
                self.cpu_record.pop()
            for item in self.waiting_queue:
                self.IO_record[item.pid][constants.END][constants.IO_END_TIME] = -1

            # 绘图信息
            ticks = []
            ylabels = []  # 生成y轴标签
            for item in self.pcb_list:
                ticks.append(item.pid)
                ylabels.append("Pid:" + str(item.pid))
            plt.yticks(ticks, ylabels, rotation=45)
            plt.title("Gantt图")
            plt.xlabel("时钟周期数")
            try:
                plt.legend(handles=[image1, image2], labels=['CPU', 'IO'])
            except:
                plt.legend(handles=[image1], labels=['CPU'])
            plt.show()

    # 进程管理模块测试指令
    # def input(self):
    #     while True:
    #         s = input(">").split()
    #         if s[0] == 'c':
    #             self.create_process('111/222/')
    #         elif s[0] == 'k':
    #             self.kill(int(s[1]))
    #         elif s[0] == 's':
    #             self.snapshot()
    #         elif s[0] == 'b':
    #             self.create('111/222/333.txt')

# if __name__ == '__main__':
# my_memory = memory_manager.MemoryManager()
# my_process_manager = process_manager(my_memory)
# test1 = threading.Thread(target=my_process_manager.run)
# test2 = threading.Thread(target=my_process_manager.input)
# test1.start()
# test2.daemon = True
# test2.start()

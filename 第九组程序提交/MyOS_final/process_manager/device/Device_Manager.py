import json
import numpy as np
import matplotlib.pyplot as plt

from .constants import *
from .Device_Storage import MsgStorage
from .IO_Message import MessageUnit


# 设备管理器
class DeviceManager:
    # 初始化函数 -------------------------------------------------------------------
    def __init__(self):
        # input，output存储数据（运行成功的进程会一一对应）
        self.task_storage = MsgStorage(TASK_SIZE)
        self.send_storage = MsgStorage(SEND_SIZE)

        # kill队列，反馈队列和错误信息队列（后两者作为反馈信息给进程）
        self.kill_list = []
        self.send_list = []
        self.error_list = []

        # 获取注册信息，字典数据类型：[size, information[], number[]]，创建设备输出字符串
        device_dict = json.loads(open('data/device_data.json', 'r', encoding='UTF-8').read())
        dict = device_dict["InputDevice"]
        self.input_devices = {"size": len(dict),
                              "information": dict,
                              "number": [-1 for _ in range(len(dict))],
                              "content": [[""] for _ in range(len(dict))]}
        dict = device_dict["OutputDevice"]
        self.output_devices = {"size": len(dict),
                               "information": dict,
                               "number": [-1 for _ in range(len(dict))],
                               "content": [[""] for _ in range(len(dict))]}

        # 图表信息数据结构初始化
        COL_SIZE = 4
        self.row = ["number", "clock", "time", "state"]
        self.col_task = np.arange(0, TASK_SIZE)
        self.val_task = [['' for j in range(COL_SIZE)] for i in range(TASK_SIZE)]
        self.col_send = np.arange(0, SEND_SIZE)
        self.val_send = [['' for j in range(COL_SIZE)] for i in range(SEND_SIZE)]


    # Before run - 放入单个任务 -----------------------------------------------------
    def task_add(self, item: MessageUnit):
        if item.type != "input" and item.type != "output":
            self.error_list.append((item.number, str(item.number)+".task.type is illegal: "+item.type))
            return False
        elif item.information == "":
            self.error_list.append((item.number, str(item.number) + ".task.information is empty: " + item.type))
            return False
        item.clock = (len(item.information)-1)//INFO_LENGTH+1
        return self.task_storage.add(item)


    # Before run - 加入删除队列 -----------------------------------------------------
    def kill_add(self, number):
        # 该删除已经有重复，必须增添错误信息
        if number in self.kill_list:
            self.error_list.append((number, "Kill "+str(number)+" repeated"))
            return False
        self.kill_list.append(number)
        return True


    # After run - 取出所有反馈信息 ----------------------------------------------------
    def send_take(self):
        # 取出所有的send_storage送到反馈队列，并清空这些消息
        for index in range(self.send_storage.size):
             self.send_list.append(self.send_storage.msg_byIndex(index))
        self.send_storage.clear()
        return (self.send_list, self.error_list)


    # After run - 去除信息后进行的清空操作 ------------------------------------------------
    def clear_afterSend(self):
        self.send_list.clear()
        self.error_list.clear()


    # Run - 每个时钟驱动一次运行函数（kill的优先级最高）-------------------------------------------
    def run(self):
        # 1 - kill任务，遍历input和output存储，删除对应的任务，并直接生成返回信息
        for number in self.kill_list:
            for item in self.task_storage.list:
                # 任务需要被删除
                if item.number == number:
                    self.send_storage.add(
                        MessageUnit(item.type, item.number, item.information, item.clock, item.time, "Has been killed"))
                    # 删除该任务
                    self.task_storage.remove(number)
                    # 在输入设备中删除任务
                    if item.type == "input":
                        if number in self.input_devices["number"]:
                            i = self.input_devices["number"].index(number)
                            self.input_devices["number"][i] = -1
                    # 在输出设备中删除任务
                    elif item.type == "output":
                        if number in self.output_devices["number"]:
                            i = self.output_devices["number"].index(number)
                            self.output_devices["content"][i].append("")  # 扩展新输出
                            self.output_devices["number"][i] = -1
                    print("Manager - killed: ", number)
                    break
        self.kill_list.clear() # kill任务结束，清空

        # 查看run之前的状态
        #print("\tDEVICE - Manager before run state:")
        #self.look_state()

        # 2 - 把所有任务存在时间 time++（任务存在于任务列表中time就要+1）
        for index in range(self.task_storage.size):
            self.task_storage.addTime_byIndex(index)

        # 3 - 输入设备进行执行，调入，调出（index遍历storage，i遍历device）
        Input_list = [] # 该时钟在执行的input任务列表
        for i in range(self.input_devices["size"]):
            # 当前设备没有被用，则选择任务调入
            if self.input_devices["number"][i] == -1:
                # 加入没运行的任务
                for index in range(self.task_storage.size):
                    item = self.task_storage.msg_byIndex(index)
                    # 这个任务不在运行，调入
                    if item.type == "input" and item.number not in self.input_devices["number"]:
                        self.input_devices["number"][i] = item.number
                        self.task_storage.convertState_byIndex(index, self.input_devices["information"][i])
                        # print("\t\tinput add task.number =", item.number)
                        break
            # 当前设备在执行任务
            if self.input_devices["number"][i] != -1:
                # 寻找当前运行任务
                for index in range(self.task_storage.size):
                    item = self.task_storage.msg_byIndex(index)
                    # 找到当前任务
                    if item.number == self.input_devices["number"][i]:
                        Input_list.append(item)  # 加入该时钟执行列表
                        self.task_storage.minusClock_byIndex(index)  # 减小这个任务的时钟周期数
                        # 时钟周期减到0，调出
                        if int(item.clock) == 0:
                            self.task_storage.remove(item.number)
                            self.send_storage.add(item)
                            # print("\t\tinput del task.number =", item.number)
                            self.input_devices["number"][i] = -1
                            break

        # 4 - 输出设备进行执行，调入，调出（index遍历storage，i遍历device）
        Output_list = [] # 该时钟在执行的output任务列表
        for i in range(self.output_devices["size"]):
            # 当前设备没有被用，则选择任务调入
            if self.output_devices["number"][i] == -1:
                # 加入没运行的任务
                for index in range(self.task_storage.size):
                    item = self.task_storage.msg_byIndex(index)
                    # 这个任务不在运行，调入
                    if item.type == "output" and item.number not in self.output_devices["number"]:
                        self.output_devices["number"][i] = item.number
                        self.task_storage.convertState_byIndex(index, self.output_devices["information"][i])
                        #print("\t\toutput add task.number =", item.number)
                        break
            # 当前设备在执行任务
            if self.output_devices["number"][i] != -1:
                # 寻找当前运行任务
                for index in range(self.task_storage.size):
                    item = self.task_storage.msg_byIndex(index)
                    # 找到当前任务
                    if item.number == self.output_devices["number"][i]:
                        Output_list.append(item)                        # 加入该时钟执行列表
                        self.task_storage.minusClock_byIndex(index)     # 减小这个任务的时钟周期数
                        # 时钟周期减到0，调出
                        if int(item.clock) == 0:
                            self.task_storage.remove(item.number)
                            self.send_storage.add(item)
                            #print("\t\toutput del task.number =", item.number)
                            self.output_devices["number"][i] = -1
                            break

        # 5 - 输出该时钟input&output处理信息
        for item in Input_list:
            print("\tDEVICE - Input running:", item.information)
        for item in Output_list:
            print("\tDEVICE - Output running:", item.information)
            # 寻找设备下标
            i = -1
            for cnt in range(self.output_devices["size"]):
                if self.output_devices["information"][cnt]["id"] == item.state["id"]:
                    i = cnt
                    break
            # 添加设备输出信息
            clocks = (len(item.information)-1)//INFO_LENGTH+1
            start_index = (clocks - item.clock - 1) * INFO_LENGTH
            if item.clock==0:
                end_index = len(item.information)-1
                self.output_devices["content"][i][len(self.output_devices["content"][i])-1] \
                    = self.output_devices["content"][i][len(self.output_devices["content"][i])-1] \
                      + item.information[start_index : end_index+1]
                self.output_devices["content"][i].append("")
            else:
                end_index = (clocks - item.clock) * INFO_LENGTH - 1
                self.output_devices["content"][i][len(self.output_devices["content"][i])-1] \
                    = self.output_devices["content"][i][len(self.output_devices["content"][i])-1] \
                      + item.information[start_index : end_index+1]
            print("device_id =", item.state["id"],"\n", self.output_devices["content"][i])


        # 查看run之后的状态
        #print("\tDEVICE - Manager after run state:")
        #self.look_state()


    # subfunction - 查看状态 ------------------------------------------------------
    def look_state(self):
        print("\t\tLook input_devices: ", self.input_devices["number"]);
        print("\t\tLook output_devices: ", self.output_devices["number"]);
        for index in range(self.task_storage.size):
            item = self.task_storage.msg_byIndex(index)
            print("\t\tLook task: type =", item.type,
                  ", number =", item.number,
                  ", information =", item.information,
                  ", clock =", item.clock,
                  ", time=", item.time,
                  ", state=", item.state)
        for index in range(self.send_storage.size):
            item = self.send_storage.msg_byIndex(index)
            print("\t\tLook send: type =", item.type,
                  ", number =", item.number,
                  ", information =", item.information,
                  ", clock =", item.clock,
                  ", time=", item.time,
                  ", state=", item.state)


    # subfunction - 生成图表 ------------------------------------------------------
    def generate_figures(self):
        # 设备当前信息数据准备
        for i in range(self.task_storage.size):
            self.val_task[i][0] = str(self.task_storage.msg_byIndex(i).number)
            self.val_task[i][1] = str(self.task_storage.msg_byIndex(i).clock)
            self.val_task[i][2] = str(self.task_storage.msg_byIndex(i).time)
            self.val_task[i][3] = self.task_storage.msg_byIndex(i).state
        for i in range(self.task_storage.size, TASK_SIZE):
            self.val_task[i][0] = "-1"
            self.val_task[i][1] = "0"
            self.val_task[i][2] = "0"
            self.val_task[i][3] = ""
        for i in range(self.send_storage.size):
            self.val_send[i][0] = str(self.send_storage.msg_byIndex(i).number)
            self.val_send[i][1] = str(self.send_storage.msg_byIndex(i).clock)
            self.val_send[i][2] = str(self.send_storage.msg_byIndex(i).time)
            self.val_send[i][3] = self.send_storage.msg_byIndex(i).state
        for i in range(self.send_storage.size, TASK_SIZE):
            self.val_send[i][0] = "-1"
            self.val_send[i][1] = "0"
            self.val_send[i][2] = "0"
            self.val_send[i][3] = ""

        fig = plt.figure(figsize=(20, 8))

        # 生成 task_storage
        ax_task = fig.add_subplot(2, 2, 1)
        ax_task.set_title('Task Storage', fontsize=20)
        plt.table(cellText=self.val_task,
                  colLabels=self.row,
                  colWidths=[0.3] * 4,
                  rowLabels=self.col_task,
                  loc='center',
                  cellLoc='center',
                  rowLoc='center')
        plt.axis('off')

        # 生成 send_storage
        ax_send = fig.add_subplot(2, 2, 2)
        ax_send.set_title('Send Storage', fontsize=20)
        plt.table(cellText=self.val_send,
                  colLabels=self.row,
                  rowLabels=self.col_send,
                  loc='center',
                  cellLoc='center',
                  rowLoc='center')
        plt.axis('off')

        # 生成output信息展示
        size = self.output_devices["size"]
        for i in range(size):
            # 生成该设备数据（最多展示10行）
            length = len(self.output_devices["content"][i])
            tmp_val = self.output_devices["content"][i]
            row = np.arange(0, length)
            if (len(self.output_devices["content"][i])) > 10:
                tmp_val = tmp_val[length-1-INFO_ROWS : len]
                row = row[length-1-INFO_ROWS : len]
            val = []
            for item in tmp_val:
                val.append([item])

            # 画图
            ax = fig.add_subplot(2, size, size+i+1)
            ax.set_title(self.output_devices["information"][i]["name"], fontsize=20)
            plt.table(cellText=val,
                      rowLabels=row,
                      loc='center',
                      cellLoc='center',
                      rowLoc='center')
            plt.axis('off')

        plt.show()
        #plt.savefig('data/device_state.jpg')
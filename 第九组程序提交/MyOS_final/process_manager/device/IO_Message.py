from .constants import *


class MessageUnit:
    def __init__(self, type=DEFAULT_TYPE, number=DEFAULT_NUMBER, information=DEFAULT_INFORMATION, clock=DEFAULT_CLOCK, time=DEFAULT_TIME, state=DEFAULT_STATE):
        # 类型， 进程数字， 传输字节内容， 放入时钟周期， IO运行时间， 运行状态
        self.type = type
        self.number = number
        self.information = information
        self.clock = clock
        self.time = time
        self.state = state
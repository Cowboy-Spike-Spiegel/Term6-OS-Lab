class Data:
    def __init__(self, string, size):
        self.string = string
        self.size = size

    def access(self, start, offset):
        step = len(self.string) / self.size
        return self.string[int(start * step): int((start + offset) * step)]
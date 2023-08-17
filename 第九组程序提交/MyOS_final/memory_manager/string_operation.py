def cutString(ret, string):
    sum = 0
    for i in ret:
        sum += i
    step = len(string) / sum
    strings = []
    flag = 0
    for i in range(len(ret)):
        strings.append(string[int(flag): int(flag + ret[i] * step)])
        flag += ret[i] * step
    return strings

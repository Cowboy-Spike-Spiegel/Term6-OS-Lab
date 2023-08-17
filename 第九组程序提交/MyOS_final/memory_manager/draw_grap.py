import matplotlib.pyplot as plt

def drawGrap(data, type):
    plt.rcParams['backend'] = 'TkAgg'  # 取消SciView显示
    plt.rcParams["font.sans-serif"] = "simhei"
    vir = []
    phy = []
    label = []
    for i in range(1, len(data)):
        data[0][0] -= data[i][1]
        data[0][1] -= data[i][2]
        vir.append(data[i][1])
        phy.append(data[i][2])
        label.append("pid=" + str(data[i][0]))
    vir.append(data[0][0])
    phy.append(data[0][1])
    label.append("FREE")
    if type == 1:
        plt.pie(vir, labels=label, autopct="%.2f%%")
        plt.title("虚拟内存使用情况")
        plt.show()
    if type == 2:
        plt.pie(phy, labels=label, autopct="%.2f%%")
        plt.title("物理内存使用情况")
        plt.show()

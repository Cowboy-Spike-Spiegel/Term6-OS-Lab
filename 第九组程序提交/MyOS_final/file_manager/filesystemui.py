import sys

from .fileSystem import *
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QListWidgetItem,QListWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QSize,Qt

class FileSystemUI(QWidget, Ui_filesystem):

    open_sig = QtCore.pyqtSignal()
    new_dir_sig =QtCore.pyqtSignal()
    del_sig = QtCore.pyqtSignal()
    new_file_sig=QtCore.pyqtSignal()
    file_attribute_sig=QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_item()
        self.path_btn.setStyleSheet("QPushButton{border-image: url(file_manager/image/back_btn.png)}")
        self.jmp_btn.setStyleSheet("QPushButton{border-image: url(file_manager/image/jmp_btn.png)}")
        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.custom_right_menu)


    def custom_right_menu(self,pos):
        menu = QtWidgets.QMenu()

        hitIndex = self.listWidget.indexAt(pos).column()

        if hitIndex > -1:
            opt1 = menu.addAction("打开")
            opt2 = menu.addAction("查看文件属性")
            opt3 = menu.addAction("删除")
            # 获取item内容
            action = menu.exec_(self.listWidget.mapToGlobal(pos))
            if action == opt1:
                self.open_sig.emit()
            elif action == opt2:
                self.file_attribute_sig.emit()
            elif action == opt3:
                self.del_sig.emit()

        else:
            opt1=menu.addAction("新建文件夹")
            opt2=menu.addAction("新建文件")
            action = menu.exec_(self.listWidget.mapToGlobal(pos))
            if action==opt1:
                self.new_dir_sig.emit()
            elif action==opt2:
                self.new_file_sig.emit()


    def path_update(self,path):

        self.path_lineedit.setText(path)


    def init_item(self):
        widget = QWidget()
        item_layout = QHBoxLayout()
        item_layout.addWidget(QLabel().setFixedSize(50, 50))
        item_layout.addWidget(QLabel('名称'))
        item_layout.addWidget(QLabel('类型'))
        item_layout.addWidget(QLabel('修改日期'))
        item_layout.addWidget(QLabel('大小'))

        widget.setLayout(item_layout)
        item = QListWidgetItem()
        item.setSizeHint(QSize(50, 50))
        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, widget)


    def addItem(self, content=[]):
        # 总Widget
        widget = QWidget()
        # 布局
        layout_item = QHBoxLayout()  # 图片横向布局

        file_name = content[0]
        file_type = content[1]
        file_time = content[2]
        file_size = content[3]




        # 图像标签
        img_l = QLabel()
        img_l.setFixedSize(50, 50)
        if file_type == '.dir':
            img_file = QPixmap('file_manager/image/dir.png').scaled(50,50,QtCore.Qt.KeepAspectRatio)
        else:
            img_file = QPixmap('file_manager/image/file.png').scaled(50,50,QtCore.Qt.KeepAspectRatio)
        img_l.setPixmap(img_file)

        # 内容填充
        layout_item.addWidget(img_l)
        layout_item.addWidget(QLabel(file_name))
        layout_item.addWidget(QLabel(file_type))
        layout_item.addWidget(QLabel(file_time))
        layout_item.addWidget(QLabel(file_size))

        widget.setLayout(layout_item)  # 为Widget设置总布局

        item = QListWidgetItem()
        item.setSizeHint(QSize(50, 50))

        # 设置item和item布局
        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, widget)


if __name__ == '__main__':
    myapp = FileSystemUI()
    app = QApplication(sys.argv)

    app.exec()

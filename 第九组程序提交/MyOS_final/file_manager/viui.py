from PyQt5.QtWidgets import QApplication,QDialog
from .viDialog import *
import sys
from PyQt5 import QtWidgets,QtCore


class ViWindow(Ui_Dialog,QDialog):
    save_signal = QtCore.pyqtSignal(str)
    def __init__(self, content):
        super().__init__()
        self.setupUi(self)

        # textEdit自动填充
        # self.setCentralWidget(self.ui.input)
        # 将文件内容添加到textEdit
        self.vi_textEdit.append(content)
        self.content=content




    def get_content(self, content):
        self.vi_textEdit.append(content)


    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        reply = QtWidgets.QMessageBox.question(self,
                                               'Vi窗口',
                                               "是否保存此次修改",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply==QtWidgets.QMessageBox.Yes:

            self.save_signal.emit(self.vi_textEdit.toPlainText())




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ViWindow(content = 'xixihaha')

    app.exec()



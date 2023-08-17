from .newDir import *
from PyQt5.QtWidgets import QDialog

class NewDirUI(QDialog,Ui_new_dir_dlg):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.cancel_btn.clicked.connect(self.cancel_btn_clicked)

    def cancel_btn_clicked(self):
        self.close()
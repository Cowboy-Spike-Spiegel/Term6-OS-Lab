from .fileattribute import *
from PyQt5.QtWidgets import QDialog

class FileAttributeUI(Ui_attribute_dialog, QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

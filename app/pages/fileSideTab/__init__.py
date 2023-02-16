import PySide6
from PySide6.QtWidgets import QWidget,QListWidgetItem
from typing import *
from ... import window

from .ui_UI import Ui_Form

class FileSideTabWidget(QWidget,Ui_Form):
    def __init__(self,app:"window.Window") -> None:
        QWidget.__init__(self,parent=None)
        self.setupUi(self)
        self.app=app

    def add_file(self,path:str):
        """添加文件"""
        self.listWidget.addItem(path)

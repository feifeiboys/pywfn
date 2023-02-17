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
        self.listWidget.itemClicked.connect(self.clicked)

    def add_file(self,path:str):
        """添加文件"""
        self.listWidget.addItem(path)

    def clicked(self,item:QListWidgetItem):
        
        path=item.text() # 轨道的序数，肯定都是整数
        fileItem=self.app.fileItems[path]
        self.app.set_layoutWidget(self.app.canvasLayout,fileItem)
        self.app.currentFile=fileItem
        fileItem.on_show()
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
        # self.listWidget.itemClicked.connect(self.clicked)
        self.listWidget.currentRowChanged.connect(self.row_changed)

    def add_file(self,path:str):
        """添加文件"""
        self.listWidget.addItem(path)

    def clicked(self,item:QListWidgetItem):
        path=item.text() # 文件路径
        self.show_file(path)
    
    def row_changed(self,row:int):
        item=self.listWidget.item(row)
        path=item.text()
        self.show_file(path)

    def show_file(self,path):
        print(path)
        fileItem=self.app.fileItems[path]
        self.app.set_layoutWidget(self.app.canvasLayout,fileItem)
        self.app.currentFile=fileItem
        fileItem.on_show()
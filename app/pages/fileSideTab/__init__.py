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
        self.molIDs:Dict[str,str]={} #记录分子路径与分子id的对应关系

    def add_file(self,path:str,molID:str):
        """添加文件"""
        self.listWidget.addItem(path)
        self.molIDs[path]=molID


    def clicked(self,item:QListWidgetItem):
        path=item.text() # 文件路径
        self.show_file(path)
    
    def row_changed(self,row:int):
        item=self.listWidget.item(row)
        path=item.text()
        self.show_file(path)

    def show_file(self,path):
        molID=self.molIDs[path]
        self.app.molView.on_show(molID)
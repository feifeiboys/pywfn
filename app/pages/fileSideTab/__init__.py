import PySide6
from PySide6.QtWidgets import QWidget,QListWidgetItem,QMenu
from PySide6.QtGui import QAction,QMouseEvent,QColor
from PySide6.QtCore import QObject,QEvent,Qt
from typing import *
from ... import window
from pathlib import Path

from .ui_UI import Ui_Form

class FileSideTabWidget(QWidget,Ui_Form):
    def __init__(self,app:"window.Window") -> None:
        QWidget.__init__(self,parent=None)
        self.setupUi(self)
        self.app=app
        # self.listWidget.itemClicked.connect(self.clicked)
        self.listWidget.currentRowChanged.connect(self.row_changed) # 行数改变时触发，既可以是点击，也可以是上下键
        self.molIDs:Dict[str,str]={} #记录分子路径与分子id的对应关系
        # self.listWidget.mousePressEvent=self.mousePressEvent
        self.installEventFilter(self)
        self.R_Menu()

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
    
    def set_runed(self,molID:str):
        """将计算完成的文件改变背景颜色"""
        path=None
        for key,value in self.molIDs.items():
            if value==molID:
                path=key
                break
        if path is None:return

        for i in range(self.listWidget.count()):
            widget=self.listWidget.item(i)
            if path==widget.text():
                widget.setBackground(QColor('#B7D332'))


    def show_file(self,path):
        molID=self.molIDs[path]
        self.app.molView.on_show(molID)
    
    def sort_list(self):
        """对列表内容进行排序"""
        self.listWidget.sortItems(Qt.AscendingOrder)
    
    def clear_list(self):
        """清空列表"""
        count=self.listWidget.count()
        items=[self.listWidget.item(i) for i in range(count)]
        for item in items:
            self.listWidget.removeItemWidget(item)

    def remove_mol(self):
        self.app.molView.remove_mol()

    def R_Menu(self):
        """定义右键菜单"""
        self.r_menu=QMenu()
        act=QAction("排序",self)
        act.triggered.connect(self.sort_list)
        self.r_menu.addAction(act)

        act=QAction("删除",self)
        act.triggered.connect(self.remove_mol)
        self.r_menu.addAction(act)
    
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        
        if event.type()==QEvent.ContextMenu:
            self.r_menu.exec(event.globalPos())
        return super().eventFilter(watched, event)

    # def mousePressEvent(self,event: QMouseEvent)->None:
    #     if event.button()==Qt.RightButton:
    #         self.r_menu.exec(event.globalPos())
    #     return super().mousePressEvent(event)
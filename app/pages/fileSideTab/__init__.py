"""
显示所有分子，数据用namedtuple保存起来
"""

import PySide6
from PySide6.QtWidgets import QWidget,QListWidgetItem,QMenu
from PySide6.QtGui import QAction,QMouseEvent,QColor
from PySide6.QtCore import QObject,QEvent,Qt
from typing import *
from ... import window
from pathlib import Path
from collections import namedtuple

from .ui_UI import Ui_Form

File=namedtuple('File',['path','molID','text']) # 定义一个namedtuple类，有分子路径，分子id和显示文本三个数据
class FileSideTabWidget(QWidget,Ui_Form):
    def __init__(self,app:"window.Window") -> None:
        QWidget.__init__(self,parent=None)
        self.setupUi(self)
        self.app=app
        # self.listWidget.itemClicked.connect(self.clicked)
        self.listWidget.currentRowChanged.connect(self.row_changed) # 行数改变时触发，既可以是点击，也可以是上下键
        self.files:List[File]=[]
        # self.listWidget.mousePressEvent=self.mousePressEvent
        self.installEventFilter(self)
        self.R_Menu()

    def get_file(self,prop,value):
        """获取某个条件符合某个值的数据"""
        for file in self.files:
            if getattr(file,prop)==value:
                return file

    def add_file(self,path:str,molID:str):
        """添加文件"""
        file=File(path=path,molID=molID,text=Path(path).name)
        self.files.append(file)
        self.listWidget.addItem(file.text)
    
    def row_changed(self,row:int):
        item=self.listWidget.item(row)
        file=self.get_file('text',item.text())
        self.show_file(file.molID)
    
    def set_runed(self,molID:str):
        """将计算完成的文件改变背景颜色"""
        file=self.get_file('molID',molID)
        for i in range(self.listWidget.count()):
            widget=self.listWidget.item(i)
            if file.text==widget.text():
                widget.setBackground(QColor('#B7D332'))


    def show_file(self,molID):
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
        item=self.listWidget.currentItem()
        self.listWidget.takeItem(self.listWidget.row(item))
        file=self.get_file('text',item.text())
        self.app.molView.remove_mol(molID=file.molID)
    
    def reset_list(self):
        """恢复列表的颜色"""
        for i in range(self.listWidget.count()):
            widget=self.listWidget.item(i)
            widget.setBackground(QColor('#FFFFFF'))

    def R_Menu(self):
        """定义右键菜单"""
        self.r_menu=QMenu()
        act=QAction("排序",self)
        act.triggered.connect(self.sort_list)
        self.r_menu.addAction(act)

        act=QAction("删除",self)
        act.triggered.connect(self.remove_mol)
        self.r_menu.addAction(act)

        act=QAction("回复",self)
        act.triggered.connect(self.reset_list)
        self.r_menu.addAction(act)
    
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        
        if event.type()==QEvent.ContextMenu:
            self.r_menu.exec(event.globalPos())

        elif event.type() == QEvent.ShortcutOverride:
            if event.key()==Qt.Key_P:
                # 导出图片
                path=Path(self.app.molView.now_path)
                name:str=str(path.parent / path.stem)
                self.app.molView.canvas.plotter.screenshot(f'{name}.png',transparent_background=False)
                self.app.addLog(f'导出成功!! {name}')
            elif event.key()==Qt.Key_R:
                # 相位反转
                self.app.molView.canvas.reverse_cloud(reset=False)
            elif event.key()==Qt.Key_B:
                # 相位恢复
                self.app.molView.canvas.reverse_cloud(reset=True)
        return super().eventFilter(watched, event)
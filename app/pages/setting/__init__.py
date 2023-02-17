from PySide6.QtWidgets import QWidget,QLabel,QGridLayout,QTableWidget,QHBoxLayout,QVBoxLayout,QLineEdit,QTableWidgetItem,QHeaderView
# from PySide6.QtCore
from PySide6.QtGui import QColor
from .ui_setting import Ui_setting
from typing import *
from ...plotter.materials import get_materials
from ... import window


import PySide6
class SettingWidget(QWidget,Ui_setting):
    def __init__(self,app:"window.Window") -> None:
        QWidget.__init__(self,parent=None)
        self.setupUi(self)
        self.materials=get_materials().materials
        self.materialNames=[]
        self.init_color()
        self.app=app
        self.tableWidget.cellClicked.connect(self.select_color)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def init_color(self):
        """初始化界面,数据驱动"""
        self.tableWidget.setRowCount(len(self.materials))
        titles=['symbol','color','metalic','roughness','opacity','diffuse','specular','size']
        for i,(symbol,material) in enumerate(self.materials.items()):
            self.materialNames.append(symbol)
            # 1.符号
            item=QTableWidgetItem(symbol)
            self.tableWidget.setItem(i,titles.index('symbol'),item)
            # 2.颜色
            item=QTableWidgetItem(material.color)
            item.setBackground(QColor(material.color))
            self.tableWidget.setItem(i,titles.index('color'),item)
            # 3.金属度
            item=QTableWidgetItem(f'{material.metalic}')
            self.tableWidget.setItem(i,titles.index('metalic'),item)
            # 4.粗糙度
            item=QTableWidgetItem(f'{material.roughness}')
            self.tableWidget.setItem(i,titles.index('roughness'),item)
            # 5.透明度
            item=QTableWidgetItem(f'{material.opacity}')
            self.tableWidget.setItem(i,titles.index('opacity'),item)
            # 6.漫反射
            item=QTableWidgetItem(f'{material.diffuse}')
            self.tableWidget.setItem(i,titles.index('diffuse'),item)
            # 7.镜面
            item=QTableWidgetItem(f'{material.specular}')
            self.tableWidget.setItem(i,titles.index('specular'),item)
            # 8.尺寸
            item=QTableWidgetItem(f'{material.size}')
            self.tableWidget.setItem(i,titles.index('size'),item)
        
    def select_color(self,row:int,colum):
        symbol=self.materialNames[row]
        material=self.materials[symbol]
        self.ctl_radius.setValue(int(material.size*10))
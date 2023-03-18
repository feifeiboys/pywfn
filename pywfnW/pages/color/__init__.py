from PySide6.QtWidgets import QWidget,QLabel,QGridLayout,QTableWidget,QHBoxLayout,QVBoxLayout,QLineEdit,QTableWidgetItem,QHeaderView,QListWidgetItem
# from PySide6.QtCore
from PySide6.QtGui import QColor,QShowEvent,QCloseEvent
from .ui_color import Ui_setting
from typing import *
from ...plotter.materials import get_materials
from ... import window

from pyvistaqt import QtInteractor
from pyvista import Plotter,Actor,PolyData,Sphere
import pyvista as pv
from collections import namedtuple
from ...utils import hex2rgb

titles=['symbol','color','metalic','roughness','opacity','diffuse','specular','size']
Material=namedtuple('Material',['color','metalic','roughness','opacity','diffuse','specular','size'])


import PySide6
class ColorPage(QWidget,Ui_setting):
    def __init__(self,app:"window.Window") -> None:
        QWidget.__init__(self,parent=None)
        self.setupUi(self)
        self.materials=get_materials()
        self.materialNames=[]
        self.init_color()
        self.app=app
        self.tableWidget.cellClicked.connect(self.set_props)
        self.tableWidget.itemChanged.connect(self.item_change)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.previewLayout=QVBoxLayout()
        self.previewFrame.setLayout(self.previewLayout)
        print('页面初始化')

    def showEvent(self, event: QShowEvent) -> None:
        """页面显示"""
        self.preview=Preview()
        self.previewLayout.addWidget(self.preview)
        return super().showEvent(event)

    def init_color(self):
        """初始化界面,数据驱动"""
        self.tableWidget.setRowCount(len(self.materials))
        titles=['symbol','color','metalic','roughness','opacity','diffuse','specular','size']
        symbols=self.materials.symbols
        for i,symbol in enumerate(symbols):
            material=self.materials[symbol]
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
    
    def item_change(self,item:QListWidgetItem):
        row=item.row()
        symbol=self.tableWidget.item(row,0).text()
        column=item.column()
        prop=titles[column]
        value=item.text()
        if symbol=='BackGround':
            self.preview.plotter.set_background()
        if prop != 'color':
            value=float(value)
        self.materials.setitem(symbol,prop,value)
        material=self.materials[symbol]
        self.preview.set_props(material)
        print('item change',item.text())

    def set_props(self,row:int,colum):
        print(row,colum)
        symbol=self.materialNames[row]
        material=self.materials[symbol]
        self.preview.set_props(material)
    
    def set_material(self,symbol:str,prop:str,value):
        """设置材质"""
        ...
    
    def closeEvent(self, event:QCloseEvent) -> None:
        self.preview.close()
        return super().closeEvent(event)


class Preview(QtInteractor):
    def __init__(self) -> None:
        super().__init__()
        self.plotter=self.interactor
        self.mesh:PolyData=pv.Sphere()
        # print(type(self.mesh))
        self.sphere:Actor=self.plotter.add_mesh(self.mesh,smooth_shading=True,pbr=True)
    
    def set_props(self,material:Material):
        """改变预览属性"""
        print(material)
        self.sphere.prop.SetColor(hex2rgb(material.color))
        self.sphere.prop.SetMetallic(material.metalic)
        self.sphere.prop.SetRoughness(material.metalic)
        self.sphere.prop.SetOpacity(material.opacity)
        # self.sphere.prop.SetNormalScale(material.size)
    
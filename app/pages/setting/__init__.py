from PySide6.QtWidgets import QWidget,QLabel,QGridLayout,QTableWidget,QHBoxLayout,QVBoxLayout,QLineEdit
from .ui_setting import Ui_Form
from typing import *
from ...plotter.materials import get_elements



import PySide6
class SettingWidget(QWidget,Ui_Form):
    def __init__(self,parent=None) -> None:
        QWidget.__init__(self,parent)
        self.setupUi(self)
        self.init_color()
    

    def init_color(self):
        """初始化界面,数据驱动"""
        layout=QGridLayout()
        
        layout.addWidget(QLabel('symbol'),0,0)
        layout.addWidget(QLabel('color'),0,1)
        layout.addWidget(QLabel('radius'),0,2)
        elements=get_elements().elements
        for i,element in enumerate(elements):
            layout.addWidget(QLabel(element.symbol),i+1,0)
            label=QLabel(element.color)
            label.setStyleSheet(f'background-color:{element.color}')
            layout.addWidget(label,i+1,1)
            layout.addWidget(QLabel(f'{element.radius:.4f}'),i+1,2)
        vlayout=QVBoxLayout()
        vlayout.addLayout(layout)
        self.color.setLayout(vlayout)

        

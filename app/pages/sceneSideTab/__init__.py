"""
定义场景侧边栏
"""
from PySide6.QtWidgets import QWidget,QListWidgetItem,QMenu
from PySide6.QtGui import QShowEvent

from .ui_UI import Ui_Form
from ... import window
from typing import *

class SceneSideTabWidget(QWidget,Ui_Form):
    def __init__(self,app:"window.Window") -> None:
        super().__init__()
        self.setupUi(self)
        self.app=app

    def update(self):
        """更新显示场景中的actor"""
        actors=self.app.molView.canvas.plotter.actors
        names=[name for name in actors]
        """添加当前场景中没有的"""
        items=[self.listWidget.item(i) for i in range(self.listWidget.count())]
        scenes=[item.text() for item in items]
        for name in names:
            if name not in scenes:
                self.listWidget.addItem(name)
        
        rms=[]
        for i,each in enumerate(scenes):
            if each not in names:
                rms.append(self.listWidget.item(i))
        for widget in rms:
            self.listWidget.removeItemWidget(widget)
    
    def showEvent(self, event: QShowEvent) -> None:
        print('showEvent',QShowEvent)
        self.update()
        return super().showEvent(event)
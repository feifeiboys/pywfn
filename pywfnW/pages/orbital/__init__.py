from PySide6.QtWidgets import QWidget,QListWidgetItem
from .ui_orbital import Ui_Form
from typing import *

# from ...window import Window
from ... import window

class OrbitalWidget(QWidget,Ui_Form):
    def __init__(self,app:"window.Window"):
        QWidget.__init__(self,parent=None)
        self.setupUi(self)
        self.app=app
        self.listWidget.itemClicked.connect(self.clicked)
        # self.itemClicked.connect(self.clicked)
    
    def set_orbitals(self,obts:List[str]):
        self.obts=obts
        self.listWidget.clear()
        self.listWidget.addItems(obts)
    
    def clicked(self,item:QListWidgetItem):
        obt=self.obts.index(item.text()) # 轨道的序数，肯定都是整数
        self.app.molView.canvas.show_cloud(obt,molIDs=[self.app.molView.canvas.molID])
        self.app.molView.showObtIdx=obt
    
    def on_show(self):
        showIdx=self.app.molView.showObtIdx
        if showIdx is not None:
            self.listWidget.setCurrentRow(showIdx)
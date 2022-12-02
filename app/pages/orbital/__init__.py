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
        self.listWidget.addItems(obts)
    
    def clicked(self,item:QListWidgetItem):
        obt=self.obts.index(item.text())
        self.app.currentFile.canvas.show_cloud(obt)
        
        print(item.text())
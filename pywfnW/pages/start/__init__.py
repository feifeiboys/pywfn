from PySide6.QtWidgets import QWidget
from .ui_start import Ui_Form

class StartWidget(QWidget,Ui_Form):
    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        self.setupUi(self)
from PySide6.QtWidgets import QWidget
from .ui_setting import Ui_Form
from typing import *
import PySide6
class SettingWidget(QWidget,Ui_Form):
    def __init__(self,parent=None) -> None:
        QWidget.__init__(self,parent)
        self.setupUi(self)
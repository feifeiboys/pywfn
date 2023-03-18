from PySide6.QtWidgets import QWidget
from .ui_start import Ui_Form

text="""
欢迎使用PyWfnW程序
点击菜单栏 file->open 即可打开文件
更多使用说明请访问 https://feifeiboys.github.io/pywfnDOC/
"""


class StartPage(QWidget,Ui_Form):
    def __init__(self,app):
        QWidget.__init__(self)
        self.setupUi(self)
        self.app=app
        self.label.setText(text)

import sys
sys.path.append('E:\code\HFV\pywfn')
import os
import PySide6
dirname = os.path.dirname(PySide6.__file__) 
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
os.environ["QT_API"] = "pyside6"

from PySide6.QtWidgets import QApplication,QStyleFactory
from PySide6.QtGui import QIcon,QFont
import sys
from app.window import Window


if __name__=='__main__':
    app=QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion")) #fusion风格
    w=Window()
    w.show()
    sys.exit(app.exec_())
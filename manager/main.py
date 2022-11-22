"""
这个程序应该比较简单,不需要进行什么运算,只需要利用pywfn的模块读取、保存、显示信息就好了
"""
import sys
from pathlib import Path
print(Path(__file__).parent)
sys.path.append(Path(__file__).parent)
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
import PySide6
dirname = os.path.dirname(PySide6.__file__) 
plugin_path = os.path.join(dirname, 'plugins', 'platforms') # 指定动态链接库的位置
print(plugin_path)
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
os.environ["QT_API"] = "pyside6"

from PySide6.QtWidgets import QWidget,QMainWindow,QApplication,QStyleFactory,QFileDialog,\
    QTableWidgetItem,QTableWidget,QTreeWidgetItem,QHeaderView
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap,QAction

from .ui_main import Ui_MainWindow
from .tools import Tools,Info,Infos
from typing import *
import time
from threading import Thread
from .rightMenu import RightMenu
from tqdm import tqdm
import multiprocessing as mp
from collections import Counter

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui=ui=Ui_MainWindow()
        ui.setupUi(self)
        ui.action_import.triggered.connect(self.import_files)
        self.setAcceptDrops(True)
        
        self.currentRoute=None #当前文件分类
        self.ui.table.itemDoubleClicked.connect(self.openFile)
        self.ui.table.itemClicked.connect(self.selectFile)
        self.ui.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.rightMenu=RightMenu(self)
    
        # self.ui.img.setScaledContents(True)
        self.ui.splitter.setStretchFactor(0,2)
        self.ui.splitter.setStretchFactor(1,6)
        self.ui.splitter.setStretchFactor(2,2)
        # self.ui.table.clear()
        self.tools=Tools(self)
        self.table=Table(self)
        self.tree=RouteList(self)
        
        self.ui.route_btn.clicked.connect(self.add_route)
    
    def add_route(self):
        name=self.ui.route_input.text()
        self.tree.add(name)

    def openFile(self,item):
        path=self.table.infos[item.row()].path
        print(path)
        os.startfile(path)
    
    def selectFile(self,item):
        info=self.table.infos[item.row()]
        self.showProp(info)
        print(info)
    
    def showProp(self,info:Info):
        """显示文件的基本信息"""
        # self.ui.text.setHtml(info.html())
        imgPath=info.folder/'mol.png'
        img=QPixmap(imgPath)#.scaled(self.ui.img.size())
        self.ui.img.setPixmap(img)
        self.ui.text.setMarkdown(info.md()) # 以markdown的形式显示信息

        
    def import_files(self):
        """导入外部文件"""
        import multiprocessing as mp
        files,fileType=QFileDialog.getOpenFileNames(self,'打开文件')
        ts=[]
        for file in files:
            t=Thread(target=self.tools.create_file,args=(file,))
            ts.append(t)
            t.start()
        for t in ts:
            t.join()
        self.tree.update()

    def dragEnterEvent(self, event) -> None:
        print('拖动事件')

    def showMsg(self,text):
        """在状态栏显示信息"""
        self.ui.statusbar.showMessage(text,500)

class RouteList:
    """最左边的文件栏是树结构"""
    def __init__(self,window:Main) -> None:
        self.window=window
        self.infos:List[Info]=window.tools.infos
        self.msgs:List[str]=[]
        self.init()

    def init(self):
        """初始化节点信息"""
        names=[]
        for info in self.infos:
            route=info.route
            name='未分类文件' if route is None else route
            names.append(name)
        
        for name in set(names):
            self.msgs.append(f'{name}-{names.count(name)}')
        
        self.show()
    
    def add(self,name):
        msg=f'{name}-0'
        if msg not in self.msgs:
            self.msgs.append(msg)
            self.show()
    
    def show(self):
        """根据节点信息显示组件内容"""
        self.window.ui.list.clear()
        for msg in self.msgs:
            self.window.ui.list.addItem(msg)
    
            
class Table:
    """
    表格这个组件本是不需要动的,需要改变的是表格的内容(当切换分类的时候)
    """
    def __init__(self,window:Main) -> None:
        self.window=window
        self.titles=['文件名','原子数量','修改时间'] # 字符串组成的列表，用于控制显示那些类型的信息
        self.infos=[]
        self.contents=[] # 字典组成的列表
        self.show(None)
    
    def show(self,route):
        infos=[]
        """显示指定路由的信息"""
        for info in self.window.tools.infos:
            if info.route==route:
                infos.append(info)
        self.set(infos)

    
    def set(self,infos:List[Info]):
        """将传入的info以列表的形式显示出来"""
        self.infos=infos
        self.window.showProp(infos[0]) # 显示第一个信息
        contents=[]
        for info in infos:
            content={}
            for title in self.titles:
                if title=='文件名':
                    content[title]=info.name
                elif title=='原子数量':
                    content[title]=f'{len(info.symbols)}'
                elif title=='修改时间':
                    content[title]=f'{time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(info.st_mtime))}'
            contents.append(content)
        self.contents=contents
        self.update()

    def update(self):
        """根据内容生成一个表格对象"""
        
        # 首先要把原来的表格清空
        table=self.window.ui.table
        # 然后根据数据生成表格内容        
        # 添加标题
        table.setColumnCount(len(self.titles)) # 设置有多少列
        table.setRowCount(len(self.contents))
        table.setHorizontalHeaderLabels(self.titles)
        # 添加内容
        for i,content in enumerate(self.contents):
            for j,title in enumerate(self.titles):
                item=QTableWidgetItem(content[title])
                item.setFlags(Qt.ItemIsEnabled)
                table.setItem(i,j,item)
        
        self.window.ui.table.resizeColumnsToContents()
        
def run():
    app=QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion")) #fusion风格
    w=Main()
    w.show()
    sys.exit(app.exec())
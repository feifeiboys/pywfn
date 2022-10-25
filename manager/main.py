"""
这个程序应该比较简单,不需要进行什么运算,只需要利用pywfn的模块读取、保存、显示信息就好了
"""
import sys
from pathlib import Path

from numpy import Inf
print(Path(__file__).parent)
sys.path.append(Path(__file__).parent)
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
import PySide6
dirname = os.path.dirname(PySide6.__file__) 
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
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

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui=ui=Ui_MainWindow()
        ui.setupUi(self)
        ui.action_import.triggered.connect(self.import_files)
        self.setAcceptDrops(True)
        self.tools=Tools()
        
        self.table=Table(self)
        self.tree=Tree(self)
        self.currentRoute=None #当前文件分类
        self.ui.table.itemDoubleClicked.connect(self.openFile)
        self.ui.table.itemClicked.connect(self.selectFile)
        self.ui.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.init_rightMenu()
        

        
        # self.ui.img.setScaledContents(True)
        self.ui.splitter.setStretchFactor(0,2)
        self.ui.splitter.setStretchFactor(1,6)
        self.ui.splitter.setStretchFactor(2,2)
        # self.ui.table.clear()
    
    def init_rightMenu(self):
        """初始化右键菜单"""
        self.ui.table.setContextMenuPolicy(Qt.ActionsContextMenu) # 允许右键菜单
        # 具体菜单项
        option = QAction(self.ui.table)
        option.setText("更新")
        option.triggered.connect(self.updateFile) # 点击菜单中的“发送控制代码”执行的函数

        # tableView 添加具体的右键菜单
        self.ui.table.addAction(option)
    
    def updateFile(self):
        item=self.ui.table.currentItem()
        info=self.table.infos[item.row()]
        info.update()
        self.tree.update()
    
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
        files,fileType=QFileDialog.getOpenFileNames(self,'打开文件')
        for file in files:
            print(f'{file=}')
            self.tools.create_file(file)
            self.update_tree()
            self.update_table()

    def dragEnterEvent(self, event) -> None:
        print('拖动事件')


class Tree:
    """最左边的文件栏是树结构"""
    def __init__(self,window:Main) -> None:
        self.nodes={} # 每一个节点是一个表格信息{route:{wid}}
        self.window=window
        self.infos=window.tools.infos
        self.currentNode=None
        self.update()

    def update(self):
        """更新节点信息"""
        self.nodes={}
        for info in self.infos:
            route=info.route
            if route not in self.nodes.keys():self.nodes[route]=[]
            self.nodes[route].append(info)
        self.window.table.set_content(self.nodes[self.currentNode])
        self.show()
    
    def show(self):
        """将节点信息显示到树组件上"""
        for key,infos in self.nodes.items():
            name=key if key is not None else '未分类文件'
            treeNode=QTreeWidgetItem()
            treeNode.setText(0,name)
            for info in infos:
                treeNode.addChild(QTreeWidgetItem([info.name]))
            self.window.ui.tree.addTopLevelItem(treeNode)
            
class Table:
    """
    表格这个组件本是不需要动的,需要改变的是表格的内容(当切换分类的时候)
    """
    def __init__(self,window:Main) -> None:
        self.window=window
        self.titles=['文件名','原子数量','修改时间'] # 字符串组成的列表，用于控制显示那些类型的信息
        self.infos=[]
        self.contents=[] # 字典组成的列表
    
    def set_content(self,infos:List[Info]):
        print(len(infos))
        self.infos=infos
        self.window.showProp(infos[0])
        contents=[]
        for info in infos:
            content={}
            for title in self.titles:
                if title=='文件名':
                    content[title]=info.name
                elif title=='原子数量':
                    content[title]=f'{info.atomNum}'
                elif title=='修改时间':
                    content[title]=f'{time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(info.st_mtime))}'
            contents.append(content)
        self.contents=contents
        print(contents)
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
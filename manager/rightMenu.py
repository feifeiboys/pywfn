# 定义右键菜单的函数
from PySide6.QtGui import QPixmap,QAction
from PySide6.QtCore import Qt
from . import main
import os
from pathlib import Path

class RightMenu:
    def __init__(self,window:"main.Main") -> None:
        self.window=window
        """初始化右键菜单"""
        self.init_table()
        self.init_list()
        # 列表的右键菜单

    def init_table(self):
        # 表格的右键菜单
        self.window.ui.table.setContextMenuPolicy(Qt.ActionsContextMenu) # 允许右键菜单
        menus={
            "更新":self.updateFile,
            "复制路径":self.copyPath,
            "查看文件夹":self.openFolder
        }
        for name,fun in menus.items():
            option = QAction(self.window.ui.table)
            option.setText(name)
            option.triggered.connect(fun) # 点击菜单中的“发送控制代码”执行的函数
            # tableView 添加具体的右键菜单
            self.window.ui.table.addAction(option)

    def init_list(self):
        self.window.ui.list.setContextMenuPolicy(Qt.ActionsContextMenu)
        menus={
            '删除':self.remove_route
        }
        for name,fun in menus.items():
            option = QAction(self.window.ui.list)
            option.setText(name)
            option.triggered.connect(fun) # 点击菜单中的“发送控制代码”执行的函数
            # tableView 添加具体的右键菜单
            self.window.ui.list.addAction(option)
    
    def remove_route(self):
        """删除一个分类"""
        ...

    def updateFile(self):
        item=self.window.ui.table.currentItem()
        info=self.window.table.infos[item.row()]
        info.update()
        self.window.tree.update()

    def copyPath(self):
        """复制文件路径"""
        import pyperclip
        item=self.window.ui.table.currentItem()
        info=self.window.table.infos[item.row()]
        path=info.path
        pyperclip.copy(path)
    
    def openFolder(self):
        """打开文件所处位置"""
        item=self.window.ui.table.currentItem()
        info=self.window.table.infos[item.row()]
        path=info.path
        os.system(f'explorer.exe {Path(path).parent}')


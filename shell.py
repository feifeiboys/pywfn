"""
通过命令行的方式执行程序
由很多页面组成，树形关系，有子页面和父页面
"""
from typing import *
class App:
    def __init__(self):
        self.filePath:str=None
        self.homepage=FilePage(self)
        self.set_page(self.homepage)

    def set_page(self,page):
        """设置当前显示的页面"""
        page.show()
        
class FilePage:
    """让用户输入文件的界面"""
    def __init__(self,app):
        self.app=app

    def show(self):
        """打印信息并等待用户输入"""
        filePath=input('输入文件名:')
        self.app.filePath=filePath

class PiBondOrderPage:
    def __init__(self,app):
        self.app=app

    

app=App()
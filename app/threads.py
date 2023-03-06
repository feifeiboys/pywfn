"""
封装一些需要异步执行的函数
"""

from PySide6.QtCore import QThread,Signal
import time
from multiprocessing import Process
from . import window
from .plotter import canvas
from typing import *
from multiprocessing import Process


class Test(QThread):
    _signal = Signal(str)
    def __init__(self) -> None:
        super().__init__()
    
    def run(self):
        for i in range(100):
            # print(i)
            time.sleep(1)

class AddMol(QThread):
    def __init__(self,app:"window.Window") -> None:
        super().__init__()
        self.app=app
        self.paths:List[str]=[]
    
    def run(self):
        """打开文件"""
        for path in self.paths:
            self.app.molView.add_mol(path)

class RenderCloud(Process):
    def __init__(self,app:"window.Window",canvas:"canvas.Canvas") -> None:
        super().__init__()
        self.app=app
        self.canvas=canvas
        self.obt:int=0
        self.showType:str='surf'
        self.atoms:List[int]=[]
        self.molID:str=None
    
    def run(self):
        # self.canvas.molID=self.molID
        if self.molID is not None:self.canvas.show_mol(self.molID)
        self.canvas.show_cloud_t(obt=self.obt,showType=self.showType,atoms=self.atoms)
"""
封装一些需要异步执行的函数
"""

from PySide6.QtCore import QThread,Signal,QRunnable,QObject
import time
from multiprocessing import Process
from . import window
from .plotter import canvas
from typing import *
from multiprocessing import Process
import numpy as np
from pywfn.base import Mol
from pywfn.readers import get_reader
from pathlib import Path
from . import signals


class AddMol(QRunnable):
    def __init__(self,app:"window.Window",path:str) -> None:
        super().__init__()
        self.app=app
        self.path=path
        self.signal:signals.OpenFile=None
    
    def run(self):
        """打开文件"""
        mol=get_reader(Path(self.path)).mol
        self.signal.sig.emit(self.path,mol)
        # self.app.molView.add_mol(self.path,mol)

class RenderCloud(QRunnable):
    def __init__(self,app:"window.Window",canvas:"canvas.Canvas",obt:int,atoms:List[int],molID:str) -> None:
        super().__init__()
        self.app=app
        self.canvas=canvas
        self.obt=obt
        self.showType:str='surf'
        self.atoms=atoms
        self.molID=molID
        self.signal:signals.RenderCloud=None
    
    def run(self):
        
        if self.showType=='surf':
            values,origin,name,molID=self.canvas.show_cloud_t(obt=self.obt,showType=self.showType,atoms=self.atoms,molID=self.molID)
            self.signal.sigSurf.emit(values,origin,name,molID)
        elif self.showType=='point':
            posP,posN,name,molID=self.canvas.show_cloud_t(obt=self.obt,showType=self.showType,atoms=self.atoms,molID=self.molID)
            self.signal.sigPoint.emit(posP,posN,name,molID)
        self.app.fileSideTab.set_runed(self.molID)
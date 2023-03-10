"""
信号用起来真麻烦，必须要是类属性
每一个事件定义一个信号
"""
from PySide6.QtCore import Signal,QObject
import numpy as np
from pywfn.base import Mol
class RenderCloud(QObject):
    sigSurf=Signal(np.ndarray,np.ndarray,str,str)
    sigPoint=Signal(np.ndarray,np.ndarray,str,str)

class OpenFile(QObject):
    sig=Signal(str,Mol)
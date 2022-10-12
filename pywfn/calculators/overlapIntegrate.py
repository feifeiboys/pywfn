# 此脚本计算重叠积分
# 重叠积分需要有两个原子，分别计算这两个原子的原子轨道
from ctypes import util
import numpy as np
from ..base import Mol,Atom
from .. import utils
class Calculator:
    def __init__(self,mol:Mol) -> None:
        self.mol=mol

    def calculate(self,a1:Atom,a2:Atom,orbital:int):
        """传入两个原子，计算重叠积分"""
        p1=a1.coord
        p2=a2.coord
        center=(p1+p2)/2
        
        radius=np.linalg.norm(p1-p2)/2
        gridPoints=utils.get_gridPoints(radius+4,0.1,ball=True)
        values_1=a1.gridValues(points=gridPoints+center.reshape(3,1),orbital=orbital)
        values_2=a2.gridValues(points=gridPoints+center.reshape(3,1),orbital=orbital)
        return np.sum(np.abs(values_1*values_2*0.1**3))
    

    

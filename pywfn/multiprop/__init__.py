"""
需要多个分子才能计算的属性
"""
from .. import base
from typing import *
from functools import cached_property,lru_cache
from ..atomprop import mullikenCharge
import numpy as np
class Fukui:
    """
    福井函数，以及依赖于福井函数计算的一些性质
    福井函数值针对原子的函数
    """
    def __init__(self,molN:"base.Mol",molM:"base.Mol",molP:"base.Mol") -> None:
        """
        需要三个分子对象
        molN:负电性分子
        molM:中性分子
        molP:正电性分子
        """
        if len(set([len(molN.atoms),len(molM.atoms),len(molP.atoms)]))!=1:
            print('三个分子的原子数量不相等')
        calerN=mullikenCharge.Calculator(molN)
        calerM=mullikenCharge.Calculator(molM)
        calerP=mullikenCharge.Calculator(molP)
        chargesN=calerN.calculate(atoms=None)
        chargesM=calerM.calculate(atoms=None)
        chargesP=calerP.calculate(atoms=None)
        self.fns=np.array(chargesM)-np.array(chargesN)
        self.fps=np.array(chargesP)-np.array(chargesM)
    
    @lru_cache
    def fn(self,idx:int):
        """获取某个原子的福井函数+"""
        return self.fns[idx-1]
    
    @lru_cache
    def fp(self,idx:int):
        """获取某个原子的福井函数-"""
        return self.fps[idx-1]

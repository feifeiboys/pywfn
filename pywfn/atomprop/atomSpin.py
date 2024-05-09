"""
此脚本用来计算mulliken自旋
自旋是α电子-β电子
可以通过改变轨道的占据情况来分别计算α和β电子数
"""

from pywfn.base import Mol,Atom
from pywfn.utils import printer
from pywfn.atomprop import atomCharge, lutils,AtomCaler
from pywfn.atomprop.atomCharge import Chrgs
from pywfn.maths import CM2PM

from typing import Literal
import numpy as np

class Calculator(AtomCaler):
    def __init__(self,mol:"Mol") -> None:
        self.mol=mol
        self.logTip='mulliken 电子自旋分布:'

    def calculate(self,chrg:Chrgs='mulliken')->np.ndarray:
        """计算所有原子的自旋"""
        assert self.mol.open,'非开壳层分子无法计算自旋'
        obtNum=self.mol.CM.shape[0] # 系数矩阵行数，基函数数量
        occs_old=self.mol.obtOccs # 记录原本的占据情况
        a_occs=occs_old.copy() # 当你需要修改一个变量的时候，
        b_occs=occs_old.copy()
        a_occs[obtNum:]=[False]*obtNum
        b_occs[:obtNum]=[False]*obtNum

        caler=atomCharge.Calculator(self.mol)

        # 将长方形的系数矩阵分为两个正方形分别计算

        self.mol.props['obtOccs']=a_occs
        a_Ects=caler.calculate(chrg=chrg)

        self.mol.props['obtOccs']=b_occs
        b_Ects=caler.calculate(chrg=chrg)
        # 恢复分子属性
        self.mol.props['obtOccs']=occs_old
        return -(a_Ects-b_Ects)
        
    def resStr(self):
        elects=self.calculate()
        atoms=lutils.atomIdxs(self.mol.atoms)
        return lutils.atomValueStr(self.mol,atoms,elects)
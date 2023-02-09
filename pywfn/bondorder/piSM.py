"""
轨道挑选法+mayer键级公式
mayer键级需要重叠矩阵,可一次性计算所有键级(此时原子的法向量由三个原子决定,而不是垂直于键轴)
"""
from ..base import Mol,Atom
from ..maths import vector_angle
from .utils import CM2PM,judgeOrbital,formPrint
import numpy as np
from . import Caler

class Calculator(Caler):
    def __init__(self,mol:Mol) -> None:
        self.mol=mol

    def calculate(self,idx1:int,idx2:int)->float:
        """指定两个原子,计算π键键级"""
        centerAtom=self.mol.atom(idx1)
        aroundAtom=self.mol.atom(idx2)
        if self.mol.CM is None:
            print('没有系数矩阵,无法计算')
            return 0
        centerNormal=centerAtom.get_Normal()
        orbitals=self.mol.O_obts
        CM_=np.zeros_like(self.mol.CM) # 拷贝一份，然后将不是π轨道的那些变成0
        atoms=[centerAtom,aroundAtom]
        piObts=[]
        for atom in atoms: # 修改每个原子对应的系数矩阵
            if atom.symbol=='H':continue
            a_1,a_2=atom.obtRange
            for orbital in orbitals:
                judgeRes=judgeOrbital(centerAtom,aroundAtom,orbital,centerNormal)
                if judgeRes!=0: # 如果是π轨道
                    CM_[a_1:a_2,orbital]=self.mol.CM[a_1:a_2,orbital]
                    piObts.append(orbital)
        oe=1 if self.mol.isOpenShell else 2
        PM_=CM2PM(CM_,orbitals,oe)
        SM=self.mol.SM
        PS=PM_@SM

        a1,a2=centerAtom.obtRange
        b1,b2=aroundAtom.obtRange
        order=np.sum(PS[a1:a2,b1:b2]*PS[b1:b2,a1:a2])
        piObts=set(piObts)
        piObts=[self.mol.obtStr[o] for o in piObts]
        formPrint(contents=[piObts],eachLength=10)
        return order

        
                    
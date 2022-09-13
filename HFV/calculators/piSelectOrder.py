# 挑选π轨道，计算π键级
from ..obj import Mol,Bond
from .. import utils
from typing import *
import numpy as np

class Caculater:

    def __init__(self,mol:Mol) -> None:
        self.mol=mol

    def judge_orbital(self,bond:Bond,orbital:int)-> int:
        """判断某一个键的分子轨道是不是π轨道,成键返回1，反键返回-1，否则返回0"""
        centerAtom=bond.a1
        aroundAtom=bond.a2
        centerNormal=centerAtom.get_Normal(aroundAtom) #法向量方向
        if len(aroundAtom.neighbors)==3:
            aroundNormal=aroundAtom.get_Normal(centerAtom)
        else:
            aroundNormal=centerNormal
        if utils.vector_angle(centerNormal,aroundNormal,trans=True)>0.5:
            aroundNormal*=-1

        centerOrbitalDirection=centerAtom.get_orbitalDirection(orbital) #原子轨道方向
        aroundOrbitalDirection=aroundAtom.get_orbitalDirection(orbital)
        if np.linalg.norm(centerOrbitalDirection)==0 or np.linalg.norm(aroundOrbitalDirection)==0:
            return 0
        centerAngle=utils.vector_angle(centerNormal,centerOrbitalDirection,trans=True)
        aroundAngle=utils.vector_angle(aroundNormal,aroundOrbitalDirection,trans=True)

        if centerAngle<0.2 and aroundAngle<0.2:
            if utils.vector_angle(centerOrbitalDirection,aroundOrbitalDirection)<=0.5:
                return 1
            else:
                return -1
        else:
            return 0

    def get_piOrbitals(self,bond:Bond)->List[int]:
        """返回该键的所有π键"""
        return [self.judge_orbital(bond,orbital) for orbital in self.mol.O_orbitals]

    def calculate(self,bond:Bond)->Tuple[float,List[float]]:
        orbitals=self.get_piOrbitals(bond)
        As=self.mol.As2
        print(As)
        centerAtom=bond.a1
        aroundAtom=bond.a2
        centerSquareSum=centerAtom.squareSum
        aroundSquareSum=aroundAtom.squareSum
        centerRes=np.divide(centerSquareSum,As,out=np.zeros_like(As),where=As!=0)**0.5
        aroundRes=np.divide(aroundSquareSum,As,out=np.zeros_like(As),where=As!=0)**0.5
        orders=(centerRes*aroundRes)[:len(self.mol.O_orbitals)]*np.array(orbitals)*self.mol.orbitalElectron
        print(self.mol.orbitalElectron)
        return list(orders),sum(orders)
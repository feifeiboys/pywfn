# 挑选π轨道，计算π键级
from ..obj import Mol,Bond,Atom
from .. import utils
from typing import *
import numpy as np

class Calculator:

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

    def get_piUnits(self,bond:Bond)->List[int]:
        """返回该键的所有π键"""
        return [self.judge_orbital(bond,orbital) for orbital in self.mol.O_orbitals]

    def calculate(self,centerAtom:Atom,aroundAtom:Atom)->Tuple[float,List[float]]:
        bond=self.mol.get_bond(centerAtom.idx, aroundAtom.idx)
        units=self.get_piUnits(bond)
        As=np.array([atom.squareSum for atom in self.mol.atoms.values()]).sum(axis=0)
        centerSquareSum=centerAtom.squareSum
        aroundSquareSum=aroundAtom.squareSum
        centerRes=np.divide(centerSquareSum,As,out=np.zeros_like(As),where=As!=0)**0.5
        aroundRes=np.divide(aroundSquareSum,As,out=np.zeros_like(As),where=As!=0)**0.5
        oE=1 if self.mol.isSplitOrbital else 2 # 每个分子轨道内的电子
        orders=(centerRes*aroundRes)[:len(self.mol.O_orbitals)]*np.array(units)*oE
        return {
                "type":1,
                "data":{
                    "orders":list(orders),
                    "order":sum(orders)
                }
                }
# 挑选π轨道，计算π键级
from ..obj import Mol,Bond,Atom
from .. import utils
from typing import *
import numpy as np

class Calculator:

    def __init__(self,mol:Mol) -> None:
        self.mol=mol
        self.ratios={}

    def judge_orbital(self,bond:Bond,orbital:int)-> int:
        """判断某一个键的分子轨道是不是π轨道,成键返回1，反键返回-1，否则返回0"""
        centerAtom=bond.a1
        aroundAtom=bond.a2
        

        centerTs=centerAtom.pLayersTs(orbital)
        aroundTs=aroundAtom.pLayersTs(orbital)
        centerPs=[np.array(centerTs[i:i+3]) for i in range(0,len(centerTs),3)]
        aroundPs=[np.array(aroundTs[i:i+3]) for i in range(0,len(aroundTs),3)]
        normal=centerAtom.get_Normal(aroundAtom)
        centerPs_=centerAtom.get_pLayersProjection(normal, orbital) # 先计算投影
        aroundPs_=aroundAtom.get_pLayersProjection(normal, orbital)
        # print(centerPs,centerPs_)
        # print(aroundPs,aroundPs_)
        centerRatio=np.linalg.norm(np.sum(np.array(centerPs_)))/np.linalg.norm(np.sum(np.array(centerPs))) #投影后与投影前的比例
        aroundRatio=np.linalg.norm(np.sum(np.array(aroundPs_)))/np.linalg.norm(np.sum(np.array(aroundPs))) #投影后与投影前的比例
        self.ratios[f'{centerAtom.idx}-{aroundAtom.idx}-{orbital}']=centerRatio
        self.ratios[f'{aroundAtom.idx}-{centerAtom.idx}-{orbital}']=aroundRatio
        centerScont=centerAtom.get_sContribution(orbital)
        aroundScont=aroundAtom.get_sContribution(orbital)
        # print(orbital,centerScont,aroundScont)
        if centerScont>0.01:
            return 0 # s贡献太大的不是
        if centerScont>0.01:
            return 0

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
        aroundAngle=utils.vector_angle(centerNormal,aroundOrbitalDirection,trans=True)

        # if centerAngle<0.2 and aroundAngle<0.2:
        if utils.vector_angle(centerOrbitalDirection,aroundOrbitalDirection)<=0.5:
            return 1
        else:
            return -1
        # else:
        #     return 0

    def get_ratios(self,center:int,around:int):
        ratios=[self.ratios[f'{center}-{around}-{o}'] for o in self.mol.O_orbitals]
        return np.array(ratios)

    def get_piUnits(self,bond:Bond)->List[int]:
        """返回该键的所有π键"""
        return [self.judge_orbital(bond,orbital) for orbital in self.mol.O_orbitals]

    def calculate(self,centerAtom:Atom,aroundAtom:Atom)->Tuple[float,List[float]]:
        bond=self.mol.get_bond(centerAtom.idx, aroundAtom.idx)
        units=self.get_piUnits(bond)
        As=np.array([atom.squareSum for atom in self.mol.atoms.values()]).sum(axis=0)
        centerSquareSum=centerAtom.squareSum
        aroundSquareSum=aroundAtom.squareSum
        centerRatios=self.get_ratios(centerAtom.idx, aroundAtom.idx)
        aroundRatios=self.get_ratios(aroundAtom.idx, centerAtom.idx)
        centerRes=np.divide(centerSquareSum,As,out=np.zeros_like(As),where=As!=0)[:len(self.mol.O_orbitals)]**0.5*centerRatios
        aroundRes=np.divide(aroundSquareSum,As,out=np.zeros_like(As),where=As!=0)[:len(self.mol.O_orbitals)]**0.5*aroundRatios
        oE=1 if self.mol.isSplitOrbital else 2 # 每个分子轨道内的电子
        # print(units)
        # print(centerRatios)
        # print(aroundRatios)
        orders=(centerRes*aroundRes)*np.array(units)*oE
        return {
                "type":1,
                "data":{
                    "orders":list(orders),
                    "order":sum(orders)
                }
                }
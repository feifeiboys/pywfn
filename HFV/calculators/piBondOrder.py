# 此脚本用来计算π建键级
from ..obj import Mol,Atom,Bond
import numpy as np
from .. import utils
from typing import *


class Calculator:
    def __init__(self,mol:Mol) -> None:
        self.mol=mol

    def get_orbitalOrder(self, center:Atom, around:Atom, orbital:int, direction): 
        '''计算两个原子间每个轨道的键级,中心原子，相邻原子，轨道，方向'''
        if around.symbol=='H':
            return 0
        if np.linalg.norm(direction)==0:
            return 0

        centerPos=center.coord
        aroundPos=around.coord
        bondVector=aroundPos-centerPos

        As = self.mol.As[orbital]
        centerTs=center.pLayersTs(orbital)
        aroundTs=around.pLayersTs(orbital)
        if np.linalg.norm(centerTs)==0 or np.linalg.norm(aroundTs)==0:
            return 0
        
        centerTs__=utils.get_projection(centerTs,bondVector,direction)
        aroundTs__=utils.get_projection(aroundTs,bondVector,direction)
        centerPZs=[each[-1].item() for each in centerTs__]
        aroundPZs=[each[-1].item() for each in aroundTs__]
        pOrder=sum([cpz*apz/As for cpz,apz in zip(centerPZs,aroundPZs)])*self.mol.orbitalElectron
        orbitalOrder=pOrder
        return orbitalOrder

    def get_orders(self,center:Atom,around:Atom,orbitals:List[int],direction):
        """计算每两个原子之间的键级"""
        orbitalNum = self.mol.orbitalNum
        orders=[self.get_orbitalOrder(center,around,orbital,direction) for orbital in orbitals] # 所有的占据轨道都计算键级
        # sortRes=sorted(zip(orbitals,orders),key=lambda s:abs(s[1]),reverse=True) # 将计算出的键级与轨道根据键级绝对值大小进行排序
        # orbitals=[each[0] for each in sortRes if abs(each[1])>9e-5]
        # orders=[each[1].item() for each in sortRes if abs(each[1])>9e-5]
        return orders

    def calculate(self,bond:Bond) -> Tuple[float,List[float]]:
        """指定一个键，计算该键的键级"""
        centerAtom=bond.a1
        aroundAtom=bond.a2
        O_orbitals=self.mol.O_orbitals
        normal=centerAtom.get_Normal(aroundAtom)
        orders=self.get_orders(centerAtom,aroundAtom,O_orbitals,normal)
        bond.piOrder=sum(orders)
        return orders,sum(orders)
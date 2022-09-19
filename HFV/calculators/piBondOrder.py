# 此脚本用来计算π建键级
from ..obj import Mol,Atom,Bond
import numpy as np
from .. import utils
from typing import *


class Calculator:
    def __init__(self,mol:Mol,orderType:str='pi') -> None: # 默认计算π键键级
        self.mol=mol
        self.orderType=orderType

    def get_orbitalOrder(self, center:Atom, around:Atom, orbital:int, direction):  # 计算一个轨道的键级
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
        if self.orderType=='pi':
            centerTs__=utils.get_projection(centerTs,bondVector,direction)
            aroundTs__=utils.get_projection(aroundTs,bondVector,direction)
        elif self.orderType=='sigma':
            centerTs__=utils.get_projection(centerTs,direction,bondVector)
            aroundTs__=utils.get_projection(aroundTs,direction,bondVector*-1)

        centerPZs=[each[-1].item() for each in centerTs__]
        aroundPZs=[each[-1].item() for each in aroundTs__]
        pOrder=sum([cpz*apz/As for cpz,apz in zip(centerPZs,aroundPZs)])*self.mol.orbitalElectron
        orbitalOrder=pOrder
        return orbitalOrder

    def get_orders(self,center:Atom,around:Atom,orbitals:List[int],direction):
        """计算每两个原子之间的键级"""
        orbitalNum = self.mol.orbitalNum
        orders=[self.get_orbitalOrder(center,around,orbital,direction) for orbital in orbitals] # 所有的占据轨道都计算键级
        return orders

    def calculateSigma(self):
        """计算sigma键级"""



    def calculate(self,bond:Bond) -> Tuple[float,List[float]]:
        """指定一个键，计算该键的键级"""
        centerAtom=bond.a1
        aroundAtom=bond.a2
        O_orbitals=self.mol.O_orbitals
        normal=centerAtom.get_Normal(aroundAtom) # 原子的法向量
        if normal is not None: # 如果原子有法向量(sp2)
            orders=self.get_orders(centerAtom,aroundAtom,O_orbitals,normal)
            bond.piOrder=sum(orders)
            return {
                "type":0,
                "data":{
                    "orders":orders,
                    "order":sum(orders)
                }
            }
        else: # 如果没有法向量的话，则需要找轨道方向作为基础方向
            # 从高到低计算轨道方向，遇到有垂直于键轴的则作为轨道方向
            orbitalDirection=None
            for o in O_orbitals[::-1]:
                orbitalDirection=centerAtom.get_orbitalDirection(o)
                bondDirection=self.mol.get_bond(centerAtom.idx, aroundAtom.idx).bondVector()
                if utils.vector_angle(orbitalDirection, bondDirection,trans=True)>0.4: # 夹角要很大
                    break
            if orbitalDirection is not None:
                orders1=self.get_orders(centerAtom,aroundAtom,O_orbitals,orbitalDirection)
                crossDirection=np.cross(orbitalDirection, bondDirection)
                orders2=self.get_orders(centerAtom,aroundAtom,O_orbitals,crossDirection)
                return {
                    "type":1,
                    "data":{
                        "orders":[orders1,orders2],
                        "order":[sum(orders1),sum(orders2)]
                    }
                }

from typing import *
import numpy as np
import pandas as pd
import re
from numpy import ndarray
from .. import utils
from .. import setting
from ..base.basis import Basi
from ..maths.gto import agto
from functools import cached_property,lru_cache
from .. import printer
"""
一个原子的轨道组合系数就是一个矩阵，行数是基函数的数量，列数是分子轨道的数量
与轨道系数相关的太多了,尽量精简
OC是该原子的轨道系数
OCI为某一列的原子轨道系数,P:bool参数用来确定是否只要P轨道的系数
一个人原子的属性应该是标准的
原子轨道layer:List[str]
原子轨道系数OC:np.ndarray
读取器直接设置这些属性
"""
class Atom:
    def __init__(self,symbol:str,coord:List[float],idx:int,mol:"Mol"): # 每个原子应该知道自己属于哪个分子
        self.symbol=symbol
        self.coord=np.array(coord)
        self._layersData={}
        self.layers:List[str]=None
        self._squareSum=None
        self.mol:"Mol"=mol
        self.idx=idx
        self.obtWays={} #存储所有分子轨道里原子轨道的方向

        self.obtMatrixRange:List[int] # 需要在分子对象中调用函数产生这个属性值
        self._sContribution:Dict={}
        self.OC:ndarray=None
    

    @cached_property
    def neighbors(self)->List["Atom"]:
        """每个原子相邻的原子有哪些，根据分子的键来判断"""
        idxs=[]
        bonds=self.mol.bonds.values()
        for bond in bonds:
            idx1,idx2=bond.idx.split('-')
            idx1,idx2=int(idx1),int(idx2) # 键的两个原子
            if idx1==self.idx:idxs.append(idx2) # 添加不是该原子的键上的原子
            if idx2==self.idx:idxs.append(idx1)
        return [self.mol.atom(idx) for idx in set(idxs)]
    
    def get_cloud(self,pos:ndarray,obt:int)->ndarray:
        """获取波函数的点云数据"""
        basi=self.mol.basis.get(self.symbol)
        res=agto(pos,basi,self.OC[:,obt],self.layers)
        return res
    
    @lru_cache
    def cloud(self,obt:int):
        """大多数情况下,原子的点云在一定范围内是相同的"""
        pos=np.random.rand(1000,3)
        return self.get_cloud(pos,obt)

    @lru_cache
    def pLayersTs(self,orbital:int):
        '''获取原子某一轨道的p层数据'''
        pIndex=[i for i,l in enumerate(self.layers) if 'P' in l]
        return self.OC[pIndex,orbital]
    
    def get_pProj(self,direction,orbital:int):
        """计算原子p系数在某个方向上的投影,返回n个三维向量"""
        if direction is None:
            raise
        ts=self.pLayersTs(orbital) # p轨道的系数
        if np.linalg.norm(direction)==0 :
            raise
        direction=direction/np.linalg.norm(direction) # 投影向量归一化
        ps=[np.array(ts[i:i+3]) for i in range(0,len(ts),3)] #每一项都是长度为3的数组
        ps_=[np.dot(p, direction)*direction for p in ps] # 轨道向量在法向量方向上的投影
        return ps_
    
    @lru_cache
    def get_Normal(self,aroundIdx:int,main:bool=True): # 一个原子应该知道自己的法向量是多少
        """
        mian:代表是否为主动调用(防止递归)
        获取原子的法向量,垂直于键轴,如果不传入另一个原子,则垂直于三个原子确定的平面\n
        1.如果该原子连接两个原子
            1.1 如果两个原子不在一条直线上,有法向量，直接返回\n
            2.2 如果两个原子在一条之下上则没有法向量
        2.如果该原子没有法向量\n
            2.1 如果相邻的原子有法向量,返回邻原子的法向量\n
            2.2 如果相邻原子没有法向量,返回None
        """
        locNum=0.001
        around=self.mol.atom(aroundIdx)
        neighbors=self.neighbors
        normal=None
        if len(neighbors)==3:
            if around is None:
                #获取中心原子到三个相邻原子的法向量
                p1,p2,p3=[(each.coord-self.coord) for each in neighbors] 
            else:
                p1,p2,p3=[(each.coord-self.coord)*(1 if each.idx==around.idx else locNum) for each in neighbors] 
            normal=utils.get_normalVector(p1,p2,p3)
        elif len(neighbors)==2:
            p2=self.coord
            p1,p3=neighbors[0].coord,neighbors[1].coord
            angle=utils.vector_angle(p1-p2,p3-p2)
            if angle>=0.01:
                normal=utils.get_normalVector(p1,p2,p3)
        elif main: #如果是在递归中调用本函数的话就不要再次递归了
            for each in neighbors:
                normal_=each.get_Normal(around=self,main=False)
                if normal_ is not None:
                    normal=normal_
                    break
                return None #如果周围原子也没有法向量的话，返回None
        return normal
    
    @lru_cache
    def get_obtWay(self,obt:int):
        """获得原子某一原子轨道的方向"""
        atomPos=self.coord
        maxPos,maxValue=utils.get_extraValue(self,obt)
        way=maxPos-atomPos
        return way/np.linalg.norm(way)

    def __repr__(self) -> str:
        x,y,z=self.coord
        return f'{self.symbol} ({x:.4f},{y:.4f},{z:.4f})'

    @lru_cache
    def get_sCont(self,orbital:int):
        """获取某个原子轨道的贡献"""
        s=self.OC[0,orbital]
        contribution=s**2/self.mol.As[orbital]
        return contribution


class Atoms(list):
    def __init__(self) -> None:
        list.__init__([])
        self.atoms=[]
    
    def __repr__(self) -> str:
        return f'Atoms:{len(self.atoms)}'
    
    
    

from .mol import Mol
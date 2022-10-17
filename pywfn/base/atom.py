from typing import *
import numpy as np
import pandas as pd
import re
from numpy import ndarray
from .. import utils
from .. import setting
print=utils.Printer()
"""
一个原子的轨道组合系数就是一个矩阵，行数是基函数的数量，列数是分子轨道的数量

"""
class Atom:
    def __init__(self,symbol:str,coord:List[float],idx:int,mol:"Mol"): # 每个原子应该知道自己属于哪个分子
        self.symbol=symbol
        self.coord=np.array(coord)
        self._coefficients=None 
        self._layersData={}
        self._squareSum=None
        self.normals={} #存储原子的法向量
        self.mol:"Mol"=mol
        self.idx=idx
        self.orbitalDirections={} #存储所有分子轨道里原子轨道的方向
        self._basisData:ndarray=None
        self.orbitalMatrixRange:List[int] # 需要在分子对象中调用函数产生这个属性值
        self._sContribution:Dict={}

    def set_layers(self,layer:str,nums:List[float]):
        layer=layer.strip()
        if layer not in self._layersData.keys():
            self._layersData[layer]=[]
        self._layersData[layer]+=nums
    
    @property
    def basisData(self):
        return self._basisData
    @basisData.setter
    def basisData(self,data:ndarray):
        self._basisData=data

    @property
    def neighbors(self)->List["Atom"]:
        """每个原子相邻的原子有哪些，根据分子的键来判断"""
        res=[]
        idxs=[]
        bonds=self.mol.bonds.values()
        for bond in bonds:
            idx1,idx2=bond.idx.split('-')
            idx1,idx2=int(idx1),int(idx2)
            if idx1==self.idx:idxs.append(idx2)
            if idx2==self.idx:idxs.append(idx1)

        for idx,atom in enumerate(self.mol.atoms()):
            idx+=1
            if idx in idxs:
                res.append(atom)
        return res
    
    @property
    def layers(self):
        '''获取该原子有哪些层'''
        return list(self._layersData.keys())
    
    def layerData(self,layer:int):
        '''获取原子某一层的数据'''
        return self._layersData[layer]

    def layersData(self,layers:List[int]):
        '''获取原子某些层的数据'''
        return self.OC.loc[layers,:].to_numpy()

    @property
    def OC(self):
        '''原子轨道组合系数'''
        if self._coefficients is None:
            self._coefficients=pd.DataFrame([self.layerData(layer) for layer in self.layers],index=self.layers)
        return self._coefficients

    @property
    def squareSum(self):
        """该原子所有层轨道系数的平方和"""
        return np.sum(self.OC.to_numpy()**2,axis=0)

    @property
    def pLayers(self):
        '''返回原子p价层符号'''
        return [layer for layer in self.layers if 'P' in layer]
    
    @property
    def spLayers(self) -> List[str]:
        '''返回原子s和p价层符号'''
        return [layer for layer in self.layers if ('P' in layer or 'S' in layer)]

    @property
    def pLayersData(self)->np.ndarray:
        return self.layersData(self.pLayers)

    @property
    def spLayersData(self):
        return self.layersData(self.spLayers)

    def pLayersTs(self,orbital:int):
        '''获取原子某一轨道的p层数据'''
        return self.pLayersData[:,orbital]
    
    def get_pLayersProjection(self,direction,orbital:int):
        """计算原子p系数在某个方向上的投影"""
        if direction is None:
            raise
        ts=self.pLayersTs(orbital) # p轨道的系数
        if np.linalg.norm(direction)==0 :
            raise
        direction=direction/np.linalg.norm(direction) # 投影向量归一化
        ps=[np.array(ts[i:i+3]) for i in range(0,len(ts),3)] #每一项都是长度为3的数组
        ps_=[np.dot(p, direction)*direction for p in ps] # 轨道向量在法向量方向上的投影
        return ps_
    
    def spLayersTs(self,orbital:int):
        '''获取原子某一轨道的sp层数据'''
        return self.spLayersData[:,orbital]

    def get_Normal(self,around:"Atom"=None): # 一个原子应该知道自己的法向量是多少
        """
        获取原子的法向量,垂直于键轴,如果不传入另一个原子,则垂直于三个原子确定的平面\n
        1.如果该原子有法向量，直接返回\n
        2.如果该原子没有法向量\n
            2.1 如果相邻的原子有法向量,返回邻原子的法向量\n
            2.2 如果相邻原子没有法向量,返回None
        """
        stand=np.array([0,0,1]) #基准方向,因为求出来的法向量都有两个方向，为了使法相统一，添加基准方向
        #如果与基准方向夹角大于90度，则方向取反
        locNum=0.001
        normal=None
        key=f'{self.idx}-{around}' if around is None else f'{self.idx}-{around.idx}'
        if key not in self.normals.keys(): # 每个原子的法向量应该只计算一次
            neighbors=self.neighbors
            if len(neighbors)==3:
                if around is None:
                    #获取中心原子到三个相邻原子的法向量
                    p1,p2,p3=[(each.coord-self.coord) for each in neighbors] 
                else:
                    p1,p2,p3=[(each.coord-self.coord)*(1 if each.idx==around.idx else locNum) for each in neighbors] 
                normal=utils.get_normalVector(p1,p2,p3)
            else:
                for each in neighbors:
                    normal_=each.get_Normal(around=self)
                    if normal_ is not None:
                        normal=normal_
                        break
                    return None #如果周围原子也没有法向量的话，返回None
            if utils.vector_angle(normal,stand)>0.5:normal*=-1
            self.normals[key]=normal
        normal=self.normals[key]
        return normal
    
    def get_orbitalDirection(self,orbital:int):
        """获得原子某一原子轨道的方向"""
        if orbital not in self.orbitalDirections.keys():
            ts=self.pLayersTs(orbital)
            atomPos=self.coord.reshape(3,1)
            paras=self.basisData
            maxPos,maxValue=utils.get_extraValue(atomPos, paras, ts, 'max')
            direction=(maxPos-atomPos).flatten()
            self.orbitalDirections[orbital]=direction
        return self.orbitalDirections[orbital]

    def __repr__(self) -> str:
        x,y,z=self.coord
        return f'{self.symbol} ({x:.4f},{y:.4f},{z:.4f})'

    def gridValues(self,points,orbital:int):
        """计算原子在指定位置的函数值"""
        values=utils.posan_function(centerPos=self.coord.reshape(3,1),aroundPos=points,paras=self.standardBasis,ts=self.pLayersTs(orbital))
        return values


    def get_sContribution(self,orbital:int):
        return self.get_sCont(orbital)
    def get_sCont(self,orbital:int):
        """获取某个原子轨道的贡献"""
        if orbital not in self._sContribution.keys():
            s=self.OC.iloc[0,orbital]
            contribution=s**2/self.mol.As[orbital]
            self._sContribution[orbital]=contribution
        return self._sContribution[orbital]


class Atoms:
    def __init__(self) -> None:
        self.atoms=[]

    def add(self,atom:Atom):
        self.atoms.append(atom)

    def __getitem__(self,key):
        return self.atoms[key]
    
    def __len__(self):
        return len(self.atoms)
    
    def __repr__(self) -> str:
        return f'Atoms:{len(self.atoms)}'
    
    
    

from .mol import Mol
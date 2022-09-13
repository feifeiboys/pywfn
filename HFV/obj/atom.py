from typing import *
import numpy as np
import pandas as pd
from numpy import ndarray
from .. import utils
class  Atom:
    def __init__(self,symbol:str,coord:List[float],idx:int,mol): # 每个原子应该知道自己属于哪个分子
        self.symbol=symbol
        self.coord=np.array(coord)
        self._coefficients=None 
        self._layersData={}
        self._squareSum=None
        self.normals={} #存储原子的法向量
        self.mol=mol
        self.idx=idx
        self.orbitalDirections={} #存储所有分子轨道里原子轨道的方向
        self.standardBasis:ndarray=None

    def set_layers(self,layer:str,nums:List[float]):
        if layer not in self._layersData.keys():
            self._layersData[layer]=[]
        self._layersData[layer]+=nums

    @property
    def neighbors(self)->List["Atom"]:
        """每个原子相邻的原子有哪些"""
        res=[]
        for idx,atom in self.mol.atoms.items():
            if idx!=self.idx:
                if np.linalg.norm(self.coord-atom.coord)<=1.7:
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
    def pLayersData(self):
        return self.layersData(self.pLayers)

    @property
    def spLayersData(self):
        return self.layersData(self.spLayers)

    def pLayersTs(self,orbital:int):
        '''获取原子某一轨道的p层数据'''
        return self.pLayersData[:,orbital]
    
    def spLayersTs(self,orbital:int):
        '''获取原子某一轨道的sp层数据'''
        return self.spLayersData[:,orbital]

    def get_Normal(self,around:"Atom"): # 一个原子应该知道自己的法向量是多少
        locNum=0.001
        if f'{self.idx}-{around.idx}' not in self.normals.keys(): # 每个原子的法向量应该只计算一次
            neighbors_i=self.neighbors
            neighbors_j=around.neighbors
            if len(neighbors_i)==3:
                p1,p2,p3=[(each.coord-self.coord)*(1 if each.idx==around.idx else locNum) for each in neighbors_i] #获取中心原子到三个相邻原子的法向量
                normal_vector_i=utils.get_normalVector(p1,p2,p3)
                if len(neighbors_j)!=3:
                    normal_vector_j=normal_vector_i
            if len(neighbors_j)==3:
                p1,p2,p3=[(each.coord-around.coord)*(1 if each.idx==self.idx else locNum) for each in neighbors_j] #获取中心原子到三个相邻原子的法向量
                normal_vector_j=utils.get_normalVector(p1,p2,p3)
                if len(neighbors_i)!=3:
                    normal_vector_i=normal_vector_j
            self.normals[f'{around.idx}-{self.idx}']=normal_vector_j
            self.normals[f'{self.idx}-{around.idx}']=normal_vector_i
        return self.normals[f'{self.idx}-{around.idx}']
    
    def get_orbitalDirection(self,orbital:int):
        """获得原子某一原子轨道的方向"""
        if orbital not in self.orbitalDirections.keys():
            ts=self.pLayersTs(orbital)
            atomPos=self.coord.reshape(3,1)
            paras=self.standardBasis
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
from typing import *
import numpy as np
import pandas as pd
import re
from numpy import ndarray
from .. import utils
from .. import setting
"""
一个原子的轨道组合系数就是一个矩阵，行数是基函数的数量，列数是分子轨道的数量

"""
class  Atom:
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
        self.standardBasis:ndarray=None
        self.orbitalMatrixRange:List[int]

    def set_layers(self,layer:str,nums:List[float]):
        layer=layer.strip()
        if layer not in self._layersData.keys():
            self._layersData[layer]=[]
        self._layersData[layer]+=nums

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

        for idx,atom in self.mol.atoms.items():
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
    def pLayersData(self):
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
        ts=self.pLayersTs(orbital)
        if np.linalg.norm(direction)==0 :
            raise
        direction=direction/np.linalg.norm(direction) # 投影向量归一化
        ps=[np.array(ts[i:i+3]) for i in range(0,len(ts),3)] #每一项都是长度为3的数组
        ps_=[np.dot(p, direction)*direction for p in ps] # 轨道向量在法向量方向上的投影
        return ps_
    
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
            if len(neighbors_i)!=3 and len(neighbors_j)!=3:
                return None # 如果两个原子连接的原子数量都不是三个的话，就没有法向量
            self.normals[f'{around.idx}-{self.idx}']=normal_vector_j
            self.normals[f'{self.idx}-{around.idx}']=normal_vector_i
        normal=self.normals[f'{self.idx}-{around.idx}']
        if normal is None:
            raise
        return normal
    
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

    def piOC(self,around:"Atom"):
        
        layers=self.OC.index # 所有的行的名称
        pidxs=[idx for idx,layer in enumerate(layers) if re.match('\dP[XYZ]',layer)] # p轨道的序数
        size=self.OC.shape[1] # 列数
        for orbital in range(len(size)): # 对每一列进行循环
            data=OC.iloc[:,orbital]
            ps_=self.get_pLayersProjection(self.get_Normal(around), orbital)



from .mol import Mol
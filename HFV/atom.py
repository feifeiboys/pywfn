from typing import *
import numpy as np
import pandas as pd
class Atom:
    def __init__(self,symbol:str,coord:List[float]):
        self.symbol=symbol
        self.coord=np.array(coord)
        self._coefficients=None
        self._layersData={}
        self._squareSum=None
        self.normals={} #存储原子的法向量

    def set_layers(self,layer:str,nums:List[float]):
        if layer not in self._layersData.keys():
            self._layersData[layer]=[]
        self._layersData[layer]+=nums
    
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

    def pLayersTs(self,orbital):
        '''获取原子某一轨道的p层数据'''
        return self.pLayersData[:,orbital]
    
    def spLayersTs(self,orbital):
        '''获取原子某一轨道的p层数据'''
        return self.spLayersData[:,orbital]
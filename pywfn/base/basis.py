"""
定义基组类，存储基组信息，方便计算波函数的时候调用
一个基组类对应于一种元素，可以根据原子类型查询基组信息
根据层分类，一个层对应一个原子轨道系数(SP的要分开)
一个层内只有高斯指数和收缩系数，都是个列表
举个例子
{
    '2P':[
        [a1,a2,a3],
        [c1,c2,c3]
    ]
}
各种基组的各个层之间的基组信息和原子轨道的名称到底是如何对应的?
每一个层应该对应两个列表,基组与层名之间应该是一一对应的
已知的层名有:
1S
2S
2PX
2PY
2PZ
3S
3PX
3PY
3PZ
4XX
4YY
4ZZ
4XY
4XZ
4YZ
"""

from typing import Dict, List, Tuple
import numpy as np

class Layer:
    """封装一层基组信息"""
    def __init__(self,name) -> None:
        self.name=name
        self._data=[]
    
    def add(self,nums:List[float]):
        self._data.append(nums)
    
    @property
    def data(self):
        if not hasattr(self,'dataArray'):
            setattr(self,'dataArray',np.array(self._data,dtype=np.float32))
        return getattr(self,'dataArray')

    def __repr__(self) -> str:
        return f'{self.name},{len(self.data)}'

class Basi:
    """封装一个原子的基组信息"""
    def __init__(self,symbol:str) -> None:
        self.symbol=symbol
        self.layers:List["Layer"]=[]
    
    def add_layer(self,name:str):
        layer=Layer(name)
        self.layers.append(layer)
        return layer
    
    def __repr__(self) -> str:
        return f'Basi:{self.symbol}'

    def get(self) -> List[Tuple[str,np.ndarray]]:
        """运算的时候获取某个原子的基组信息"""
        return [(l.name,l.data) for l in self.layers]


class Basis:
    """封装一个分子的基组信息"""
    def __init__(self):
        self.data:Dict[str:Basi]={}
        
    def get(self,symbol:str)->"Basi":
        return self.data[symbol]
    
    def new(self,symbol:str):
        if symbol in self.data.keys(): #如果这个元素的基组信息已经存在了，就不需要再读取了
            return False
        else:
            basi=Basi(symbol)
            self.data[symbol]=basi
            return True
    
    def __repr__(self) -> str:
        basis=self.data.values()
        return ','.join([f'{e.symbol}' for e in basis])
    





        


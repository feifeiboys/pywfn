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

!! 不从文件中读取信息啦, 而是根据基组名称直接获取信息
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

# class Basi:
#     """封装一个原子的基组信息"""
#     def __init__(self,symbol:str) -> None:
#         self.symbol=symbol
#         self.layers:List["Layer"]=[]
    
#     def add_layer(self,name:str):
#         layer=Layer(name)
#         self.layers.append(layer)
#         return layer
    
#     def __repr__(self) -> str:
#         return f'Basi:{self.symbol}'

#     def get(self) -> List[Tuple[str,np.ndarray]]:
#         """运算的时候获取某个原子的基组信息"""
#         return [(l.name,l.data) for l in self.layers]


# class Basis:
#     """封装一个分子的基组信息"""
#     def __init__(self):
#         self.data:Dict[str:Basi]={}
        
#     def get(self,symbol:str)->"Basi":
#         return self.data[symbol]
    
#     def new(self,symbol:str):
#         if symbol in self.data.keys(): #如果这个元素的基组信息已经存在了，就不需要再读取了
#             return False
#         else:
#             basi=Basi(symbol)
#             self.data[symbol]=basi
#             return True
    
#     def __repr__(self) -> str:
#         basis=self.data.values()
#         return ','.join([f'{e.symbol}' for e in basis])
    


import basis_set_exchange as bse
from itertools import product
from functools import cached_property,lru_cache

"""
一个原子的基组应该有一下层级

不同价层
    指数(一维数组)
    系数(二维数组)
不同角动量对应不同的mnl
所有可能的m+n+l=角动量决定了基函数的数量

"""

class Basis:
    
    def __init__(self,basiName:str) -> None:
        # 基组名有时候需要翻译
        transDict={
            '6-31G(d)':'6-31G*'
        }
        if basiName in transDict.keys():
            basiName=transDict[basiName]

        self.name=basiName

    @lru_cache
    def lmn(self,ang:int)->list:
        """
        根据角动量获取l,m,n
        基函数中包含 x^l.y^m.z^n
        """
        res=[]
        Rs=range(ang+1)
        for l,m,n in product(Rs,Rs,Rs):
            if l+m+n==ang:res.append([l,m,n])
        return res
    
    @lru_cache
    def get(self,atomic:int):
        """根据原子系数获取基组信息"""
        shells=bse.get_basis(self.name, elements=atomic)['elements'][f'{atomic}']['electron_shells']
        res=[]
        for shell in shells:
            res.append({
                'exp':np.array(shell['exponents'],dtype=np.float32),
                'coe':np.array(shell['coefficients'],dtype=np.float32),
                'ang':shell['angular_momentum'],
            })
        return res
    
    def num(self,atomic:int):
        """获取基组原子对应的基函数数量"""
        shells=self.get(atomic)
        number=0
        for shell in shells:
            for ang in shell['ang']:
                lmn=self.lmn(ang)
                number+=len(lmn)
        return number


        


# 定义各种原子的颜色
from pathlib import Path
from typing import *
import json
from functools import lru_cache

class Elements:
    def __init__(self):
        self.sym2idx={}
        self.elements:List[Element]=[]
        path=Path(__file__).parent / 'elements.json'
        with open(path,'r',encoding='utf-8') as f:
            elements=json.loads(f.read())
        for element in elements[:55]:
            idx=element['atomicNumber']
            symbol=element['symbol']
            colorStr=element['cpkHexColor']
            color=f"#{colorStr:0>6}"
            radius=float(element['atomicRadius'])/77/2 #以C原子半径为0.5作为基准
            self.elements.append(Element(idx,symbol,color,radius))
            self.sym2idx[symbol]=int(idx)
    
    def __getitem__(self,item):
        if isinstance(item,int):
            for element in self.elements:
                if element.idx==item:
                    return element
        elif isinstance(item, str):
            for element in self.elements:
                if element.symbol==item:
                    return element
        

class Element:
    def __init__(self,idx,symbol,color,radius):
        self.idx=idx
        self.symbol=symbol
        self.color=color
        self.radius=radius


@lru_cache
def get_elements()->Elements:
    return Elements()
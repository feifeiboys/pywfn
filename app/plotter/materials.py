# 定义各种原子的颜色
import pandas as pd
from pathlib import Path
from typing import *
class Elements:
    def __init__(self):
        data=pd.read_csv(Path(__file__).parent / 'elements.csv')
        self.elements:List[Element]=[]
        for i in range(data.shape[0]):
            idx,symbol,color,radius=data.iloc[i,:]
            self.elements.append(Element(idx, symbol, color, radius))
    
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

if __name__=='__main__':
    data=pd.read_csv(Path(__file__).parent.parent/'data/elements.csv')
    for i in range(len(data)):
        idx,symbol,color,radius=data.iloc[i,:]
        print(idx,symbol,color,radius)
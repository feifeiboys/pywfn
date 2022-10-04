import json
from typing import *
from pathlib import Path
import pandas as pd

class Elements:
    def __init__(self) -> None:
        self.elements=[]
        self.scriptPath=Path(__file__) #当前脚本所在的路径
        self.data=pd.read_csv(self.scriptPath.parent / 'elements.csv')
        for i in range(len(self.data)):
            idx,symbol,color,radius=self.data.iloc[i,:]
            self.elements.append(Element(idx,symbol,color,radius))

    def get_element_by_idx(self,idx:int):
        for each in self.elements:
            if each.idx==idx:
                return each
        return None

    def get_element_by_symbol(self,symbol:str):
        for each in self.elements:
            if each.symbol==symbol:
                return each
        return None

class Element:
    def __init__(self,idx,symbol,color,radius):
        self.idx=int(idx)
        self.symbol=symbol
        self.color=color
        self.radius=radius